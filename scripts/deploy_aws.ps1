param(
    [Parameter(Mandatory = $true)]
    [string]$BucketName,

    [string]$Profile = "wistia-project",
    [string]$Region = "us-east-1",
    [string]$StackName = "wistia-video-analytics"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$CandidateAwsDirs = @(
    (Join-Path $RepoRoot ".aws"),
    (Join-Path (Split-Path $RepoRoot -Parent) ".aws")
)

foreach ($AwsDir in $CandidateAwsDirs) {
    $CredentialsPath = Join-Path $AwsDir "credentials"
    $ConfigPath = Join-Path $AwsDir "config"
    if ((Test-Path -LiteralPath $CredentialsPath) -and (Test-Path -LiteralPath $ConfigPath)) {
        $env:AWS_SHARED_CREDENTIALS_FILE = $CredentialsPath
        $env:AWS_CONFIG_FILE = $ConfigPath
        break
    }
}

aws cloudformation deploy `
    --profile $Profile `
    --region $Region `
    --stack-name $StackName `
    --template-file infra/cloudformation/wistia_analytics.yml `
    --parameter-overrides BucketName=$BucketName `
    --capabilities CAPABILITY_NAMED_IAM
