param(
    [Parameter(Mandatory)][ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._@-]*$')][string] $SshTarget,
    [Parameter(Mandatory)][string] $IdentityFile,
    [string] $Destination = (Join-Path $env:USERPROFILE 'KFATA-Secure-Backups'),
    [switch] $SkipDesktopAlert
)

$ErrorActionPreference = 'Stop'
[void][IO.Directory]::CreateDirectory($Destination)
$statusPath = Join-Path $Destination 'automatic-status.json'
$process = [Diagnostics.ProcessStartInfo]::new((Get-Command ssh.exe).Source)
$process.CreateNoWindow = $true
$process.UseShellExecute = $false
$process.RedirectStandardOutput = $true
$process.RedirectStandardError = $true
foreach ($argument in @('-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes', '-o', 'StrictHostKeyChecking=yes',
    '-o', 'ConnectTimeout=15', '-o', 'ServerAliveInterval=20', '-o', 'ServerAliveCountMax=3',
    '-i', $IdentityFile, $SshTarget)) {
    $process.ArgumentList.Add($argument)
}

function Save-Status($Outcome, $Detail) {
    $next = "$statusPath.new"
    @{ timeUtc = [DateTime]::UtcNow.ToString('o'); result = $Outcome; detail = $Detail } |
        ConvertTo-Json -Compress | Set-Content -LiteralPath $next -Encoding utf8
    [IO.File]::Move($next, $statusPath, $true)
}

$stream = [IO.MemoryStream]::new()
try {
    $ssh = [Diagnostics.Process]::Start($process)
    $stderr = $ssh.StandardError.ReadToEndAsync()
    $ssh.StandardOutput.BaseStream.CopyTo($stream)
    $ssh.WaitForExit()
    [void]$stderr.GetAwaiter().GetResult()
    if ($ssh.ExitCode -ne 0 -or $stream.Length -le 17) { throw 'Exporter unavailable, stale or invalid.' }
    $payload = $stream.ToArray()
    $separator = [Array]::IndexOf($payload, [byte]10)
    if ($separator -ne 16) { throw 'Invalid snapshot response.' }
    $snapshot = [Text.Encoding]::ASCII.GetString($payload, 0, $separator)
    if ($snapshot -notmatch '^[0-9]{8}T[0-9]{6}Z$') { throw 'Invalid snapshot name.' }
    $archive = [byte[]]::new($payload.Length - $separator - 1)
    [Buffer]::BlockCopy($payload, $separator + 1, $archive, 0, $archive.Length)
    $target = Join-Path $Destination "$snapshot.tar.dpapi"
    $digest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($archive))
    if ([IO.File]::Exists($target)) {
        $cipher = [IO.File]::ReadAllBytes($target)
    } else {
        $cipher = [Security.Cryptography.ProtectedData]::Protect($archive, $null, 'CurrentUser')
    }
    $roundTrip = [Security.Cryptography.ProtectedData]::Unprotect($cipher, $null, 'CurrentUser')
    $verifiedDigest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($roundTrip))
    if ($verifiedDigest -ne $digest) { throw 'Encrypted backup did not match the server archive.' }
    if (-not [IO.File]::Exists($target)) {
        $pending = "$target.$PID.pending"
        [IO.File]::WriteAllBytes($pending, $cipher)
        [IO.File]::Move($pending, $target)
    }
    Save-Status 'ok' $snapshot
    Write-Output "Verified encrypted KFATA snapshot $snapshot"
} catch {
    Save-Status 'error' 'The encrypted KFATA backup could not be verified.'
    if (-not $SkipDesktopAlert) {
        try {
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $notice = [Windows.Forms.NotifyIcon]::new()
            $notice.Icon = [Drawing.SystemIcons]::Warning
            $notice.Visible = $true
            $notice.ShowBalloonTip(7000, 'KFATA backup', 'Backup verification failed. Open the KFATA backup status file.', 'Warning')
            Start-Sleep -Seconds 8
            $notice.Dispose()
        } catch {
            # The status file and nonzero task result are still available.
        }
    }
    throw 'KFATA encrypted backup verification failed. See automatic-status.json.'
} finally {
    if ($ssh) { $ssh.Dispose() }
    foreach ($buffer in @('payload', 'archive', 'roundTrip')) {
        $value = Get-Variable $buffer -ValueOnly -ErrorAction SilentlyContinue
        if ($value) { [Array]::Clear($value) }
    }
    $stream.Dispose()
}
