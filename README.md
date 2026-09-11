# CLTCheck

A small, read-only macOS developer-tools preflight for confusing `invalid active developer path` and missing `xcrun` failures. It explains system selection versus `DEVELOPER_DIR`, clang lookup, and macOS SDK availability without executing a compiler or repairing your Mac.

## Run

macOS with its built-in zsh; no Homebrew or Python required to run.

```sh
curl -fL https://github.com/00xmorty/cltcheck/releases/download/v0.1.0/cltcheck -o cltcheck
# Inspect the downloaded script before running it.
zsh ./cltcheck
zsh ./cltcheck --require-xcode
```

Alternatively clone this repository and run `zsh ./cltcheck`. `--require-xcode` adds a full-Xcode layout check; ordinary CLT users should omit it. `--help` and `--version` work on Linux too.

Checks report PASS, FAIL or UNKNOWN. Exit 0 means the limited checks passed, 1 means an observed directory/layout problem, and 2 means an unknown lookup, unsupported OS, or invalid usage. UNKNOWN takes precedence over FAIL. A lookup failure does not prove CLT is uninstalled.

If an override is set, compare manually with `env -u DEVELOPER_DIR zsh ./cltcheck`. A broken system selection is still reported even if the override works. Reports omit actual paths, environment values, labels and raw tool errors.

## Native-first next steps

Inspect `xcode-select -p` locally and consult [Apple's command-line tools settings](https://developer.apple.com/documentation/xcode/configuring-command-line-tools-settings). Check that your intended Xcode or CLT installation exists. If CLT is truly absent, `xcode-select --install` is a manual installation option, not a command this tool runs. Do not delete developer directories as a first response to an unknown lookup.

## Safety

- No sudo, install, delete, service changes, compiler execution, telemetry, clipboard access, or network requests by the tool.
- Only fixed absolute system commands: `uname`, `env`, `xcode-select -p`, and `xcrun --no-cache` with lookup-only flags. No `eval` and no commands constructed from user input.
- `xcrun` is Apple's tool; its internal behavior is outside this script's control. No cache invalidation is requested. Run only in trusted local environments.
- Path values and tool stderr are deliberately not printed. Review output before sharing; no automated uploads.

## Limitations

This is a wrapper around native diagnostics, not a repair utility or proof of build success. It does not check Git, Xcode licenses, first-launch completion, toolchain integrity, architecture compatibility, all SDKs, or managed-device policies. Full-Xcode detection is a directory-layout heuristic, not product validation. Directory and executable checks use the current user's access. `TOOLCHAINS` and other native xcrun environment effects are not individually diagnosed. A native lookup can block; Ctrl-C cancels it. Linux supports fixture tests and an explicit unsupported result, not live macOS diagnostics.

## Development

Python 3 is needed for tests only. All fixtures are synthetic; no actual private diagnostic captures are in the repository.

```sh
zsh -n cltcheck
python3 -m unittest discover -s tests -v
zsh ./cltcheck
```

CI runs fixture tests on macOS/Linux and the real macOS CLI on a hosted runner. Linux CI unpacks distro zsh packages in a temporary directory without root or system installation.

MIT licensed. See SECURITY.md for responsible reporting.
