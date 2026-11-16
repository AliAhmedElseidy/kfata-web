param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._@-]*$')]
    [string] $SshTarget,
    [Parameter(Mandatory)]
    [ValidatePattern('^[0-9]{8}T[0-9]{6}Z$')]
    [string] $Snapshot,
    [string] $Destination = (Join-Path $env:USERPROFILE 'KFATA-Secure-Backups')
)

$ErrorActionPreference = 'Stop'
$root = '/opt/kfata-web'
$source = "$root/backups/$Snapshot"
$target = Join-Path $Destination "$Snapshot.tar.dpapi"
if (Test-Path -LiteralPath $target) {
    throw 'An encrypted file with this snapshot name already exists.'
}

$process = [Diagnostics.ProcessStartInfo]::new((Get-Command ssh.exe).Source)
$process.CreateNoWindow = $true
$process.UseShellExecute = $false
$process.RedirectStandardOutput = $true
foreach ($argument in @('-o', 'BatchMode=yes', $SshTarget,
    "test -f '$source/.complete' && cd '$source' && sha256sum --check --status SHA256SUMS && tar -cf - -C '$root' .env -C '$source' database.dump files.tar.gz commit.txt image-id.txt SHA256SUMS")) {
    $process.ArgumentList.Add($argument)
}
$stream = [IO.MemoryStream]::new()
$ssh = [Diagnostics.Process]::Start($process)
try {
    $ssh.StandardOutput.BaseStream.CopyTo($stream)
    $ssh.WaitForExit()
    if ($ssh.ExitCode -ne 0 -or $stream.Length -eq 0) {
        throw 'KFATA backup transfer failed.'
    }
    $clear = $stream.ToArray()
    $cipher = [Security.Cryptography.ProtectedData]::Protect($clear, $null, 'CurrentUser')
    $roundTrip = [Security.Cryptography.ProtectedData]::Unprotect($cipher, $null, 'CurrentUser')
    $digest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($clear))
    $restoredDigest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($roundTrip))
    if ($digest -ne $restoredDigest) {
        throw 'Encrypted backup verification failed.'
    }
    [void][IO.Directory]::CreateDirectory($Destination)
    $file = [IO.File]::Open($target, 'CreateNew', 'Write', 'None')
    try { $file.Write($cipher, 0, $cipher.Length) } finally { $file.Dispose() }
    Write-Output "Encrypted and verified: $target"
} finally {
    if ($clear) { [Array]::Clear($clear) }
    if ($roundTrip) { [Array]::Clear($roundTrip) }
    $stream.Dispose()
    $ssh.Dispose()
}
