#!/usr/bin/env python3
from aws_cdk import (
	aws_autoscaling as autoscaling,
	aws_ec2 as ec2,
	aws_elasticloadbalancingv2 as elbv2,
	App, CfnOutput, Stack,
	aws_iam
)

import os


class LastSrcStack(Stack):
	def __init__(self, app: App, id: str) -> None:
		super().__init__(app, id)

		vpc = ec2.Vpc(self, "VPC")
		ssm_role = self.create_ssm_role()

		user_data = self.get_user_data_to_serve_simple_site()
		asg = self.create_autoscaling_group(user_data, vpc, ssm_role)
		self.create_load_balancer(asg, vpc)

	def create_ssm_role(self):
		"""Create role which allows to connect to ec2 by ssm manager"""
		return aws_iam.Role(
			self,
			'ec2-role', assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
			managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore')])

	def get_user_data_to_serve_simple_site(self):
		current_folder = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(current_folder, "httpd.sh")
		data = open(file_path, "rb").read()
		httpd = ec2.UserData.for_linux()
		httpd.add_commands(str(data, 'utf-8'))
		return httpd

	def create_autoscaling_group(self, user_data, vpc, ssm_role):
		asg = autoscaling.AutoScalingGroup(
			self,
			"ASG",
			vpc=vpc,
			instance_type=ec2.InstanceType.of(
				ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
			),
			machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
			user_data=user_data,
			role=ssm_role
		)
		return asg

	def create_load_balancer(self, asg, vpc):
		lb = elbv2.ApplicationLoadBalancer(
			self, "LB",
			vpc=vpc,
			internet_facing=True)
		listener = lb.add_listener("Listener", port=80)
		listener.add_targets("Target", port=80, targets=[asg])

		listener.add_action(
			'static',
			priority=5,
			conditions=[
				elbv2.ListenerCondition.path_patterns(["/static"])
			],
			action=elbv2.ListenerAction.fixed_response(
				200,
				content_type="text/html",
				message_body='<h1>Static ALB Response</h1>'),
		)
		listener.connections.allow_default_port_from_any_ipv4("Open to the world")

		CfnOutput(self, "LoadBalancer", export_name="LoadBalancer", value=lb.load_balancer_dns_name)
