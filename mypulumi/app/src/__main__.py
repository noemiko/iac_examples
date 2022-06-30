import pulumi_aws as aws
import pulumi


class Stack:

	def __init__(self):
		vpc = aws.ec2.get_vpc(default=True)  # it should be new but it is not easy to extract subnets
		vpc_subnets = aws.ec2.get_subnet_ids(vpc_id=vpc.id)

		alb_group = self.create_alb_security_group(vpc)
		instance_group = self.create_instance_security_group(vpc, "instance_group", alb_group)
		profile = self.create_ssm_profile_instance()
		lb, target_group = self.create_load_balancer(vpc.id, alb_group.id, vpc_subnets.ids)
		user_data = self.get_user_data_to_serve_simple_site()
		self.create_autoscaling_group(user_data, instance_group, target_group, profile)

		pulumi.export("url", lb.dns_name)

	def get_user_data_to_serve_simple_site(self):
		return """#!/bin/bash
				echo \"Hello, World!\" > index.html
				echo "<div><center><h2>Welcome AWS $(hostname -f) </h2>" >> index.html
				nohup python -m SimpleHTTPServer 80 &
				"""

	def create_instance_security_group(self, vpc, name, alb_security_group):
		return aws.ec2.SecurityGroup(
			name,
			description="Enable HTTP Access",
			vpc_id=vpc.id,
			ingress=[
				aws.ec2.SecurityGroupIngressArgs(
					security_groups=[alb_security_group],
					protocol="tcp",
					from_port=80,
					to_port=80,
					cidr_blocks=["0.0.0.0/0"]
				),
			],
			egress=[
				aws.ec2.SecurityGroupEgressArgs(
					protocol=aws.ec2.ProtocolType.ALL,
					from_port=-1,
					to_port=-1,
					cidr_blocks=["0.0.0.0/0"],
					description="Allow all outbound traffic by default"
				)
			],
		)

	def create_alb_security_group(self, vpc):
		return aws.ec2.SecurityGroup(
			"alb-web-secgrp",
			description="Enable HTTP Access",
			vpc_id=vpc.id,
			ingress=[
				{
					"protocol": "icmp",
					"from_port": 8,
					"to_port": 0,
					"cidr_blocks": ["0.0.0.0/0"],
				},
				{
					"protocol": "tcp",
					"from_port": 80,
					"to_port": 80,
					"cidr_blocks": ["0.0.0.0/0"],
				},
			],
			egress=[
				{
					"protocol": "tcp",
					"from_port": 80,
					"to_port": 80,
					"cidr_blocks": ["0.0.0.0/0"],
				}
			],
		)

	def create_ssm_profile_instance(self):
		"""Create role which allows to connect to ec2 by ssm manager"""
		testSSMRole = aws.iam.Role(
			"testSSMRole",
			assume_role_policy={
				"Version": "2012-10-17",
				"Statement": {
					"Effect": "Allow",
					"Principal": {"Service": "ec2.amazonaws.com"},
					"Action": "sts:AssumeRole"
				}
			})

		aws.iam.RolePolicyAttachment(
			"testSSMAttach",
			policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
			role=testSSMRole)

		return aws.iam.InstanceProfile("testSSMProfile", role=testSSMRole)

	def create_load_balancer(self, vpc_id, security_group_id, vpc_subnets_id):
		lb = aws.lb.LoadBalancer(
			"loadbalancer",
			internal=False,
			security_groups=[security_group_id],
			subnets=vpc_subnets_id,
			load_balancer_type="application",
		)

		target_group = aws.lb.TargetGroup(
			"target-group", port=80, protocol="HTTP", target_type="instance", vpc_id=vpc_id
		)

		aws.lb.Listener(
			"listener",
			load_balancer_arn=lb.arn,
			port=80,
			default_actions=[{"type": "forward", "target_group_arn": target_group.arn}],
		)
		return lb, target_group

	def create_autoscaling_group(self, user_data, instance_security_group, target_group, instance_profile):
		ami = aws.ec2.get_ami(
			most_recent="true",
			owners=["amazon"],
			filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-ebs"]}])

		launch_template = aws.ec2.LaunchConfiguration(
			"pulumi-launch",
			name_prefix="pulumi-ec2",
			instance_type="t3.micro",
			image_id=ami.id,
			user_data=user_data,
			security_groups=[instance_security_group],
			iam_instance_profile=instance_profile
		)
		ag = aws.autoscaling.Group(
			"as-group",
			max_size=2,
			min_size=2,
			launch_configuration=launch_template.name,
			availability_zones=aws.get_availability_zones().names
		)
		aws.autoscaling.Attachment(
			"autoscaling-attachment",
			lb_target_group_arn=target_group,
			autoscaling_group_name=ag.id
		)


Stack()
