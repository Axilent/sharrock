"""
No actual models in Sharrock, but this file is used as a Django hook to kick off descriptor registration.
"""
from saaspire.sharrock import registry
registry.build_registry()
