# Create Auto Scaling Group
resource "aws_autoscaling_group" "Demo-ASG-tf" {
  name		     = "Demo-ASG-tf"
  desired_capacity   = 2
  max_size           = 2
  min_size           = 1
  force_delete       = true
  depends_on 	     = [aws_lb.ALB-tf]
  target_group_arns  =  ["${aws_lb_target_group.TG-tf.arn}"]
  health_check_type  = "EC2"
  launch_configuration = aws_launch_configuration.webserver-launch-config.name
  vpc_zone_identifier = ["${aws_subnet.prv_sub1.id}","${aws_subnet.prv_sub2.id}"]

 tag {
    key                 = "Name"
    value               = "Demo-ASG-tf"
    propagate_at_launch = true
    }
}