from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipe4.adapters.ai.deterministic import DeterministicInterpreter
from pipe4.adapters.ai.gateway import HttpAIGatewayAdapter, UnavailableAIAdapter
from pipe4.adapters.evidence.local import LocalEvidenceStore
from pipe4.adapters.standalone.acquisition import FixtureAcquisitionConnector
from pipe4.adapters.standalone.authorization import StandaloneAuthorizationAdapter
from pipe4.adapters.standalone.clock import SystemClock
from pipe4.adapters.standalone.entities import StandaloneEntityCatalog, StandaloneLocator
from pipe4.adapters.standalone.jobs import InlineJobScheduler
from pipe4.adapters.standalone.notifications import LoggingNotificationAdapter
from pipe4.adapters.standalone.provenance import StandaloneProvenanceAdapter, StandaloneSourceRegistry
from pipe4.adapters.standalone.usage import AllowAllUsageAdapter
from pipe4.application.access import AccessService
from pipe4.application.acquisition import AcquisitionService
from pipe4.application.current_state import CurrentStateService
from pipe4.application.declarations import DeclarationService
from pipe4.application.disputes import DisputeService
from pipe4.application.entities import EntityResolutionService
from pipe4.application.nearby import NearbyService
from pipe4.application.observations import ObservationService
from pipe4.application.presentation import PresentationService
from pipe4.application.publication import PublicationService
from pipe4.application.resolution import ResolutionService
from pipe4.application.targeted_acquisition import TargetedAcquisitionService
from pipe4.application.verification import VerificationService
from pipe4.application.watches import WatchService
from pipe4.application.witness import WitnessService
from pipe4.config import Settings
from pipe4.domain.policies.confidence import ConfidenceEngine
from pipe4.domain.policies.contradiction import ContradictionEngine
from pipe4.domain.policies.decision import DecisionEngine
from pipe4.domain.policies.freshness import FreshnessEngine
from pipe4.domain.policies.nearby import NearbyRankingEngine
from pipe4.domain.policies.registry import PolicyRegistry
from pipe4.domain.policies.source_ranking import SourceRankingEngine
from pipe4.domain.policies.verification import VerificationPolicy
from pipe4.domain.policies.config import load_policy_bundle
from pipe4.api.auth import AuthVerifier


@dataclass
class ApplicationContainer:
    settings: Settings
    policies: PolicyRegistry
    auth_verifier: AuthVerifier
    repositories: object
    provenance: object
    sources: object
    entities: object
    locator: object
    authorization: object
    usage: object
    notifications: object
    jobs: object
    event_publisher: object | None
    evidence_store: object
    ai: object
    connectors: dict[str, object]

    presentation: PresentationService
    publication: PublicationService
    resolution: ResolutionService
    current_state: CurrentStateService
    declarations: DeclarationService
    disputes: DisputeService
    observations: ObservationService
    verification: VerificationService
    access: AccessService
    watches: WatchService
    entity_resolution: EntityResolutionService
    witness: WitnessService
    nearby: NearbyService
    targeted: TargetedAcquisitionService
    acquisition: AcquisitionService

    async def close(self) -> None:
        engine=getattr(self,'engine',None)
        if engine is not None: await engine.dispose()
        redis=getattr(self,'redis',None)
        if redis is not None: await redis.aclose()


def _services(*, settings, policies, repositories, provenance, sources, entities, locator, authorization, usage, notifications, jobs, event_publisher, evidence_store, ai, connectors) -> ApplicationContainer:
    clock=SystemClock(); confidence=ConfidenceEngine(policies); freshness=FreshnessEngine(policies); decision=DecisionEngine(policies); ranking=SourceRankingEngine(policies); nearby_ranking=NearbyRankingEngine(policies); contradiction_engine=ContradictionEngine(); verification_policy=VerificationPolicy(policies)
    presentation=PresentationService(authorization=authorization,entities=entities,provenance=provenance,access=repositories)
    publication=PublicationService(repository=repositories,policies=policies,clock=clock,jobs=jobs)
    verification=VerificationService(observations=repositories,states=repositories,contradictions=repositories,provenance=provenance,sources=sources,confidence=confidence,verification=verification_policy,contradiction_engine=contradiction_engine,publication=publication,events=repositories,policies=policies,clock=clock)
    resolution=ResolutionService(requests=repositories,acquisition=repositories,sources=sources,ranking=ranking,events=repositories,clock=clock,jobs=jobs)
    current=CurrentStateService(states=repositories,freshness=freshness,decision=decision,presentation=presentation,clock=clock,resolution=resolution)
    declarations=DeclarationService(authorization=authorization,provenance=provenance,sources=sources,confidence=confidence,publication=publication,clock=clock)
    observations=ObservationService(observations=repositories,provenance=provenance,sources=sources,events=repositories,clock=clock,jobs=jobs)
    disputes=DisputeService(states=repositories,observations=observations,resolution=resolution)
    access=AccessService(repository=repositories,authorization=authorization,events=repositories,clock=clock)
    watches=WatchService(repository=repositories,authorization=authorization,notifications=notifications,events=repositories,clock=clock)
    entity_resolution=EntityResolutionService(entities)
    witness=WitnessService(entities=entity_resolution,observations=observations,deterministic=DeterministicInterpreter(),ai=ai,evidence_store=evidence_store)
    nearby=NearbyService(states=repositories,entities=entities,authorization=authorization,presentation=presentation,ranking=nearby_ranking,requests=repositories,watches=repositories,clock=clock)
    targeted=TargetedAcquisitionService(repository=repositories,state_requests=repositories,events=repositories,clock=clock)
    acquisition=AcquisitionService(acquisition=repositories,requests=repositories,observations=repositories,sources=sources,connectors=connectors,provenance=provenance,evidence_store=evidence_store,verification=verification,clock=clock)
    return ApplicationContainer(settings=settings,policies=policies,auth_verifier=AuthVerifier(settings),repositories=repositories,provenance=provenance,sources=sources,entities=entities,locator=locator,authorization=authorization,usage=usage,notifications=notifications,jobs=jobs,event_publisher=event_publisher,evidence_store=evidence_store,ai=ai,connectors=connectors,presentation=presentation,publication=publication,resolution=resolution,current_state=current,declarations=declarations,disputes=disputes,observations=observations,verification=verification,access=access,watches=watches,entity_resolution=entity_resolution,witness=witness,nearby=nearby,targeted=targeted,acquisition=acquisition)


def build_memory_container(*, policy_path: Path | None=None, settings: Settings | None=None) -> ApplicationContainer:
    from pipe4.adapters.persistence.memory import InMemoryRepositories
    settings=settings or Settings(policy_path=policy_path or Path('config/policies/pipe4-policy.v1.yaml'),enable_dev_fixtures=True)
    policies=PolicyRegistry(load_policy_bundle(settings.policy_path)); repos=InMemoryRepositories(); provenance=StandaloneProvenanceAdapter(); sources=StandaloneSourceRegistry(policies); entities=StandaloneEntityCatalog(repos,clock=SystemClock()); locator=StandaloneLocator(repos); authz=StandaloneAuthorizationAdapter(repos); jobs=InlineJobScheduler(); evidence=LocalEvidenceStore(settings.evidence_local_root); ai=UnavailableAIAdapter(); connectors={'fixture':FixtureAcquisitionConnector()} if settings.enable_dev_fixtures else {}
    return _services(settings=settings,policies=policies,repositories=repos,provenance=provenance,sources=sources,entities=entities,locator=locator,authorization=authz,usage=AllowAllUsageAdapter(),notifications=LoggingNotificationAdapter(),jobs=jobs,event_publisher=None,evidence_store=evidence,ai=ai,connectors=connectors)


async def build_production_container(settings: Settings) -> ApplicationContainer:
    from redis.asyncio import Redis
    from pipe4.adapters.persistence.database import create_engine_and_session
    from pipe4.adapters.persistence.sql import SqlRepositories
    from pipe4.adapters.persistence.provenance import SqlProvenanceAdapter, SqlSourceRegistry
    from pipe4.adapters.persistence.entities import SqlEntityCatalog, SqlLocator
    from pipe4.adapters.events.redis import RedisEventPublisher
    from pipe4.adapters.standalone.redis_usage import RedisUsageAdapter
    from pipe4.adapters.jobs.celery import CeleryJobScheduler
    from pipe4.workers.celery_app import celery_app
    from pipe4.adapters.evidence.s3 import S3EvidenceStore
    policies=PolicyRegistry(load_policy_bundle(settings.policy_path)); engine,factory=create_engine_and_session(settings.database_url); repos=SqlRepositories(factory); provenance=SqlProvenanceAdapter(factory,secret=settings.internal_api_token.encode()); sources=SqlSourceRegistry(factory,policies); entities=SqlEntityCatalog(factory,clock=SystemClock()); locator=SqlLocator(factory); authz=StandaloneAuthorizationAdapter(repos); redis=Redis.from_url(settings.redis_url,decode_responses=True); publisher=RedisEventPublisher(redis); jobs=CeleryJobScheduler(celery_app)
    if settings.evidence_backend.lower() in {'s3','r2'}:
        if not settings.evidence_bucket: raise RuntimeError('PIPE4_EVIDENCE_BUCKET is required for s3/r2 evidence backend')
        evidence=S3EvidenceStore(bucket=settings.evidence_bucket,endpoint_url=settings.evidence_endpoint_url,access_key_id=settings.evidence_access_key_id,secret_access_key=settings.evidence_secret_access_key)
    else: evidence=LocalEvidenceStore(settings.evidence_local_root)
    ai=HttpAIGatewayAdapter(url=settings.ai_gateway_url,token=settings.ai_gateway_token) if settings.ai_gateway_url else UnavailableAIAdapter();connectors={'fixture':FixtureAcquisitionConnector()} if settings.enable_dev_fixtures else {}
    container=_services(settings=settings,policies=policies,repositories=repos,provenance=provenance,sources=sources,entities=entities,locator=locator,authorization=authz,usage=RedisUsageAdapter(redis,settings),notifications=LoggingNotificationAdapter(),jobs=jobs,event_publisher=publisher,evidence_store=evidence,ai=ai,connectors=connectors);container.engine=engine;container.redis=redis;return container
