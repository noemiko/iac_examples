#!/usr/bin/env python3

from aws_cdk import (
	App,
)
from code.src_stack import LastSrcStack

app = App()

LastSrcStack(app, "elbscalingec2")

app.synth()
