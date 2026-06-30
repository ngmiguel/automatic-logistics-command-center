param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("shared", "auth", "fleet", "routing", "tracking", "notification", "analytics", "simulator", "worker", "integration", "all")]
    [string]$Module
)

$args = @("scripts/tests/run_module.py", $Module)
if ($Module -eq "all") { $args += "--cov" }
python @args
