<script lang="ts">type Props={title:string;open?:boolean;children:import('svelte').Snippet};let{title,open=true,children}:Props=$props();</script>
<details class="panel" {open}><summary>{title}<span aria-hidden="true">⌄</span></summary><div class="panel-body">{@render children()}</div></details>
