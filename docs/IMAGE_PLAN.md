# Reusable G0 image plan (not yet executed)

The image is created only after the pinned Euler build, axiom printout, and unmodified Comparator/NanoDa check pass. Snapshot/image existence is not evidence of a mathematical gate pass.

1. Record source/toolchain/dependency pins, frozen-statement hashes, exact commands, exit codes, binary versions/hashes and verification logs. Flush completed build artifacts. Do not stop/restart the user's working C4 VM without separate approval.
2. Take a private project disk snapshot, recording the source disk ID and verification evidence. An online snapshot is crash-consistent; do not call it an application-quiesced or reboot-tested image without those tests.
3. Create a disposable disk from that snapshot and attach it to the small analysis VM for offline preparation. Never sanitize the live C4 filesystem. Verify the attached disk resource, device, partition and mountpoint before modifying the copy.
4. Remove copied BB identity/provider configuration, Tailscale state, SSH host/user keys, cloud CLI credentials, transient enrollment scripts and machine-specific service/session state from the offline copy without reading secret values. Reset machine-id and cloud-init instance state appropriately. Preserve Lean/toolchains, pinned public source and compiled proof artifacts. Record cleanup paths and nonsecret absence checks. No provider or mesh credential may become part of the reusable image.
5. Unmount/detach the prepared disk and create a private GCE image; document exact disk/image/snapshot provenance. Bootstrap future workers with fresh machine identities, explicit enrollment and fresh provider configuration. Never let two machines share BB or Tailscale identity.
6. Validate artifact hashes/pins from the image (and, if feasible, a disposable validation instance) before reporting it reusable. No new research worker is launched into Phase1 automatically.

Intermediate raw snapshots are private and potentially contain the original machine's credentials. They must not be shared as reusable images. Cleanup of billed intermediate resources and any disruptive validation actions should be explicitly approved rather than silently deleting unrelated resources.
