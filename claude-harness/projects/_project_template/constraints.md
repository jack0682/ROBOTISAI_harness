# Constraints — <project name>

> Hard limits for this project. The gates here are also encoded in
> `project.config.yaml` and should be respected by `protocols/file_management.md`.

## Gates (must match project.config.yaml)
- `allow_file_creation`: <true/false>
- `allow_file_deletion`: <true/false>
- `require_plan_before_edit`: <true/false>
- `require_checkpoint_for_long_task`: <true/false>

## Technical constraints
<Languages, versions, platforms, dependencies that are fixed.>

## MCP / external tools
<Required MCP servers and external tools (must match `project.config.yaml`
`mcp:`), and the fallback when one is unavailable.>

## Environment constraints
<Where this runs; resource limits; access boundaries.>

## Never break
<Conditions that must always hold — invariants, contracts, safety limits.>

## Out of bounds
<Actions explicitly forbidden in this project.>
