param(
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Layers='1',
    [string]$Config='v1/config/local_reference.json',
    [ValidateRange(1,4)][int]$Jobs=1
)
$ErrorActionPreference='Stop'
$projectRoot=$PSScriptRoot
$modelPython=Join-Path $projectRoot 'envs/model/Scripts/python.exe'
if(-not (Test-Path -LiteralPath $modelPython)) { throw 'Run python v1/scripts/bootstrap_env.py --dataset first.' }
Push-Location -LiteralPath $projectRoot
try {
    & $modelPython v1/scripts/run.py $Target --layers $Layers --jobs $Jobs --config $Config
    $taskExitCode=$LASTEXITCODE
} finally { Pop-Location }
exit $taskExitCode
