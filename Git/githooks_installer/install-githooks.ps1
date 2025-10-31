<#
Simple PowerShell installer for Windows developers.
Usage:
  .\scripts\install-githooks.ps1
  .\scripts\install-githooks.ps1 -ForceCopy
#>

param(
  [switch]$ForceCopy
)

# Ensure we are inside a git repo
try {
  git rev-parse --git-dir | Out-Null
} catch {
  Write-Error "Not a git repository. Run from inside the repo."
  exit 1
}

$repoRoot = git rev-parse --show-toplevel
Set-Location $repoRoot

$hooksDir = ".githooks"
if (-not (Test-Path $hooksDir)) {
  Write-Error "$hooksDir not found. Create hooks first."
  exit 2
}

Write-Output "Making hooks executable where applicable..."
Get-ChildItem -Path $hooksDir -File -Recurse | ForEach-Object {
  try { icacls $_.FullName /grant "${env:USERNAME}:(RX)" /C | Out-Null } catch {}
}

Write-Output "Configuring git core.hooksPath = $hooksDir"
git config core.hooksPath $hooksDir

if ($ForceCopy) {
  Write-Output "Copying hooks to .git/hooks as fallback..."
  New-Item -ItemType Directory -Path .git/hooks -Force | Out-Null
  Copy-Item -Path "$hooksDir\*" -Destination .git/hooks -Force -Recurse
}

Write-Output "Done. To uninstall: git config --unset core.hooksPath"