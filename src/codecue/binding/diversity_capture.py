"""Private durable capture adapter for the novel 5,760-case diversity bank.

No legacy module globals change. Effective batches double the previous defaults,
while hardware headroom still uses the original reference batch sizes and actual
prepared token lengths. The runner never shrinks a cohort or batch automatically.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

from . import schedule_capture as previous
from . import schedule_diversity_programs as programs
from . import relationship_schedule_programs as source_base
from . import relationships
from .datasets import digest
from .programs import rename

ROLE='discovery_diversity_capture_v1'
DATASET_ROLE=programs.ROLE
DATASET_SHA256='d43c5c3cbb5d9d3f8982a2659d4a5bde5ba5767ad143b766763ca133ee5acbc1'
SOURCE_ROWS=5760
SITES=previous.SITES
PROFILES=deepcopy(previous.PROFILES)
INSTRUCTION=previous.INSTRUCTION
RECORD_FIELDS=tuple(dict.fromkeys((*previous.RECORD_FIELDS,
    'canonical_graph_sha256','graph_selection_index','profile_id','update_count_profile',
    'destination_update_counts','slot_rotation')))

_CORE=previous._isolated_engine()
_CORE.ROLE=ROLE
_CORE.DATASET_ROLE=DATASET_ROLE
_CORE.PROFILES=deepcopy(PROFILES)
_CORE.RECORD_FIELDS=RECORD_FIELDS
_durable_config=_CORE._config
_durable_dataset=_CORE._dataset
_VALIDATED={}


def _config(config):
    if not isinstance(config,dict) or 'dataset_manifest_sha256' not in config:
        raise ValueError('explicit pinned diversity source manifest required')
    checksum=config['dataset_manifest_sha256']
    if (not isinstance(checksum,str) or len(checksum)!=64
            or any(c not in '0123456789abcdef' for c in checksum)):
        raise ValueError('explicit diversity manifest SHA256 required')
    if config.get('dataset_sha256')!=DATASET_SHA256:
        raise ValueError('exact frozen 5760-row diversity source bank required')
    if len(json.dumps(config,allow_nan=False).encode())>16*1024:
        raise ValueError('bounded complete diversity configuration required')
    if any(not isinstance(config.get(key),str) for key in ('dataset','run_dir')):
        raise ValueError('explicit diversity source/output path strings required')
    trimmed={key:value for key,value in config.items() if key!='dataset_manifest_sha256'}
    if trimmed.get('model') in PROFILES:
        trimmed.setdefault('batch_size',2*PROFILES[trimmed['model']]['batch_size'])
    recipe,folder=_durable_config(trimmed)
    if recipe['layers']!=PROFILES[recipe['model']]['layers']:
        raise ValueError('four prospectively fixed diversity capture layers required')
    dataset=Path(config['dataset']).resolve();out=folder.resolve()
    for source in (dataset,dataset.with_suffix('.manifest.json')):
        if source==out or source in out.parents or out in source.parents:
            raise ValueError('diversity source files and capture directory cannot overlap')
    return recipe,folder


def _validate_row(row):
    slots=source_base.SLOTS
    if (not isinstance(row,dict) or row.get('evaluation_role')!=DATASET_ROLE
            or row.get('condition')!='neutral' or row.get('split') not in ('train','development')
            or row.get('source_form')!='literal' or row.get('variable_slots')!=slots):
        raise ValueError('neutral literal TRAIN/DEV diversity source records required')
    for key in ('id','source','canonical_source','component_id'):
        if not isinstance(row.get(key),str) or not row[key] or len(row[key])>16384:
            raise ValueError('bounded full diversity source identity required')
    graph=row.get('canonical_graph_sha256')
    if (not isinstance(graph,str) or len(graph)!=64 or any(c not in '0123456789abcdef' for c in graph)
            or row['component_id']!='schedule-diversity-graph:'+graph[:24]
            or any(row.get(key)!=row['component_id'] for key in ('cluster_id','template_id','ssa_graph_canonical_id'))):
        raise ValueError('explicit canonical diversity graph identity required')
    seed=row.get('numeric_seed');lexical=row.get('lexical_realization');rotation=row.get('slot_rotation')
    query=row.get('query_slot');index=row.get('graph_selection_index')
    if (type(seed) is not int or seed not in programs.NUMERIC_SEEDS
            or type(lexical) is not int or lexical not in (0,1)
            or type(rotation) is not int or rotation not in range(4)
            or type(index) is not int or index not in range(20)
            or row['split']!=('train' if index<15 else 'development')
            or type(query) is not int or query not in range(4) or row.get('query_role')!=f'v{query}'
            or row.get('query_count')!=1 or row.get('base_id')!=f"{row['component_id']}:numeric{seed}"
            or row.get('paired_group_id')!=row['base_id']
            or row.get('raw_template_id')!=f"{row['component_id']}:rotation{rotation}"):
        raise ValueError('actual diversity selection, rotation, numeric/query or pairing metadata differs')
    stem='item' if lexical==0 else 'cell'
    mapping={name:f'{stem}_{slot}' for name,slot in slots.items()}
    canonical=relationships._tree(row['canonical_source']);surface=relationships._tree(row['source'])
    if (row.get('rename_map')!=mapping or len(row['source'].splitlines())!=9
            or ast.dump(relationships._tree(rename(row['canonical_source'],mapping)))!=ast.dump(surface)):
        raise ValueError('exact neutral canonical/surface diversity source required')
    destinations,parents=programs._shape(row['canonical_source'])
    profile=programs._profile(destinations)
    if (profile not in programs.PROFILES or row.get('update_count_profile')!=list(profile)
            or row.get('profile_id')!='_'.join(map(str,profile))
            or row.get('destination_update_counts')!=[destinations.count(slot) for slot in range(4)]
            or row.get('destination_schedule')!=list(destinations) or row.get('copy_parent_slots')!=list(parents)
            or row.get('parent_pattern')!='independent_distinct_slot_choices'
            or programs._graph(destinations,parents)!=graph
            or not isinstance(canonical.body[-1].value,ast.Name) or canonical.body[-1].value.id!=f'v{query}'):
        raise ValueError('actual diversity profile, rotation graph or queried source differs')
    if row['id']!='schedule-diversity:'+digest([seed,row['source']])[:24]:
        raise ValueError('case ID does not identify its actual numeric/surface source')


def _dataset(config):
    _config(config)
    manifest_path=Path(config['dataset']).with_suffix('.manifest.json')
    manifest=_CORE._json(manifest_path,config['dataset_manifest_sha256'])
    if (manifest.get('targets_prepared_only') is not True or manifest.get('learned_readout_compatible') is not False
            or manifest.get('rows')!=SOURCE_ROWS or manifest.get('canonical_graph_families')!=60
            or manifest.get('split_canonical_graph_units')!={'train':45,'development':15}
            or manifest.get('slot_complete_version_domain') is not True):
        raise ValueError('complete slot-complete diversity target-preparation manifest required')
    rows,review=_durable_dataset(config)
    if (len(rows)!=SOURCE_ROWS or review['components']!={'train':45,'development':15}
            or review['split_rows']!={'train':4320,'development':1440}
            or review['dataset_manifest_sha256']!=config['dataset_manifest_sha256']):
        raise ValueError('exact grouped diversity source cohort required')
    key=(config['dataset_sha256'],config['dataset_manifest_sha256'])
    if key not in _VALIDATED:
        checked=programs.validate_rows(manifest['generation_config'],rows,independent=False)
        if (checked['cross_split_overlap']!=manifest['cross_split_overlap']
                or checked['canonical_graph_overlap_with_named_banks']!=0
                or checked['train_minimum_current_version_class_graph_groups']<3
                or checked['maximum_assignment_version']!=4):
            raise ValueError('published diversity recipe or generic SSA/class support differs')
        _VALIDATED[key]=True
    review.update(canonical_graph_families=60,split_canonical_graph_units={'train':45,'development':15},
        count_profiles=[list(profile) for profile in programs.PROFILES],slot_complete_version_domain=True,
        slot_rotations=4,maximum_assignment_version=4,source_targets_prepared_only=True,
        existing_fixed_readouts_compatible=False,actual_generic_ssa_labels_validated=True,
        hardware_headroom_reference_batch=PROFILES[review['recipe']['model']]['batch_size'])
    return rows,review


_CORE._config=_config
_CORE._validate_row=_validate_row
_CORE._dataset=_dataset

metadata=_CORE.metadata
prepare=_CORE.prepare
run=_CORE.run
audit=_CORE.audit
completed_metadata=_CORE.completed_metadata
inputs=_CORE.inputs
load_chunk=_CORE.load_chunk
validate_chunk=_CORE.validate_chunk
layout_case=_CORE.layout_case
memory_requirements=_CORE.memory_requirements
_json=_CORE._json
