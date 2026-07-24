# Complete QSO Subsystem Tree

```text
quantum-state-objects/
├── README.md
├── STRUCTURE.md
├── spec/
│   ├── QSO-FORMAT-STANDARD.md
│   ├── MUTATION-AND-LIFECYCLE.md
│   ├── CANONICALIZATION.md
│   ├── PACKAGING.md
│   ├── STREAMING.md
│   ├── VERSIONING.md
│   └── INTEROPERABILITY.md
├── registry/
│   ├── formats.json
│   ├── media-types.json
│   ├── extensions.json
│   ├── mutation-classes.json
│   └── algorithms.json
├── schemas/
│   ├── common/qso-envelope.schema.json
│   ├── core/qso-core.schema.json
│   ├── object/{manifest,identity,self,agent,genome,relation}.schema.json
│   ├── cognitive/{state,memory,cognition,objective,mutation,evolution}.schema.json
│   ├── governance/{ethics,governance,policy,contract,legal,standard}.schema.json
│   ├── operational/{capability,workflow,plan,task,code,executable,unikernel,result}.schema.json
│   ├── scientific/{model,world,scene,simulation,experiment,sensor,tensor,field,topology,cohomology,quantum,superposition,planck}.schema.json
│   ├── transport/{communication,protocol,transport,language,media,package,bundle}.schema.json
│   ├── security/{security,key,signature,verify,evidence,provenance}.schema.json
│   └── storage/{snapshot,delta,patch,lock,archive,compressed,schema,ontology,graph,registry,index,report}.schema.json
├── profiles/
│   ├── minimal.profile.json
│   ├── autonomous-agent.profile.json
│   ├── research-object.profile.json
│   ├── governed-self-modifying.profile.json
│   └── unikernel.profile.json
├── examples/
│   ├── minimal/
│   ├── agent/
│   ├── research/
│   ├── mutation/
│   ├── signed/
│   └── bundles/
├── tools/
│   ├── qso_validate.py
│   ├── qso_pack.py
│   ├── qso_unpack.py
│   ├── qso_hash.py
│   ├── qso_sign.py
│   ├── qso_verify.py
│   ├── qso_migrate.py
│   └── qso_registry.py
├── tests/
│   ├── test_envelope.py
│   ├── test_registry.py
│   ├── test_mutation_policy.py
│   ├── test_round_trip.py
│   ├── conformance/
│   └── invalid/
└── docs/
    ├── ARCHITECTURE.md
    ├── SECURITY.md
    ├── GOVERNANCE.md
    ├── IMPLEMENTATION-GUIDE.md
    ├── THREAT-MODEL.md
    └── ROADMAP.md
```

Git tracks files rather than empty directories. Each directory enters the repository when its first normative schema, tool, example, or test is added.
