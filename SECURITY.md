# Security Policy

## Scope

This repository contains architecture documentation, a whitepaper,
benchmark results, and a small, dependency-free (numpy only) toy reference
implementation (`toy_demo/`). It does not contain the production system's
adapters, credentials, or any deployed service — so the realistic security
surface here is narrow: the toy demo's own code and its dependency chain.

## Supported Versions

This is an early-stage, single-version research/reference repository. Only
the latest commit on the default branch is supported.

## Reporting a Vulnerability

If you find a security issue in the toy demo code (or a supply-chain issue
in its declared dependencies), please report it privately rather than
opening a public issue:

- Use GitHub's [private vulnerability reporting](../../security/advisories/new)
  for this repository, or
- Contact the maintainer directly — see [`README.md`](README.md) for
  current contact links.

Please include: a description of the issue, steps to reproduce, and the
potential impact. We'll acknowledge reports within a reasonable time and
credit reporters (if desired) once a fix is out.
