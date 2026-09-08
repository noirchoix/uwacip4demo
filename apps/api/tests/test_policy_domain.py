from pathlib import Path
import pytest
from pydantic import ValidationError
from pipe4.domain.policies.config import load_policy_bundle, PolicyBundle
from pipe4.domain.state.enums import StateType
from pipe4.domain.state.identity import StateIdentity
from pipe4.domain.state.values import QuantityStateValue

def test_policy_bundle_registers_exactly_five_domains(policy_path):
    bundle=load_policy_bundle(policy_path);assert set(bundle.state_types)==set(StateType) and StateType.CHANGED in bundle.state_types

def test_policy_hash_is_deterministic(policy_path):
    a=load_policy_bundle(policy_path);b=load_policy_bundle(policy_path);assert a.content_hash==b.content_hash

def test_cold_storage_capacity_uses_horizontal_available_domain():
    identity=StateIdentity(entity_id='cold-store-1',state_type=StateType.AVAILABLE,qualifiers={'product':'vaccines','temperature_band':'2-8C'});value=QuantityStateValue(available=120,total_capacity=200,unit='litre');assert identity.state_type==StateType.AVAILABLE and value.kind=='quantity'
