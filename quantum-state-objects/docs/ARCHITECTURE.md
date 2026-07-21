# QSO Architecture

The subsystem has four layers: envelope, family payload, composition graph, and package/transport. Resolvers validate the envelope, resolve every required reference, verify hashes, detect forbidden cycles, apply profiles, and only then expose executable entrypoints. Mutation authority is established by governance objects, signatures, current policy, and mutation class—not possession of a file.
