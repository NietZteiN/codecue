# source this in every job. Only CODECUE_*-prefixed roots: the cluster exports an unwritable
# SCRATCH, and an unprefixed name silently keeps the cluster's value on compute nodes.
export CODECUE_ROOT=/work/jvl210002/migration/codecue
export CODECUE_OUT=/scratch/juno/jvl210002/codecue
export CODECUE_ENV=/work/jvl210002/migration/envs/probe-cu129
export HF_HOME=/scratch/juno/jvl210002/hf_home
export HF_HUB_OFFLINE=1
export TMPDIR=/scratch/juno/jvl210002/tmp
export PYTHONUNBUFFERED=1
export PYTHONPATH=$CODECUE_ROOT/src
export PATH=$CODECUE_ENV/bin:$PATH
mkdir -p "$CODECUE_OUT" "$TMPDIR"
