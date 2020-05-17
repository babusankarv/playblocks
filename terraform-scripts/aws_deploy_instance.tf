provider "aws" {
  region  = "us-east-2"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners = ["aws-marketplace"]
 
  filter {
    name = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server*"]
  }
  
  
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "allow_ssh_http" {
  name        = "allow_ssh"
  description = "Allow SSH and HTTP inbound traffic"

  ingress {
    description = "SSH from VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTP from VPC"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_ssh_http"
  }
}

resource "aws_instance" "my_web_server" {
  ami      = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  security_groups = ["${aws_security_group.allow_ssh_http.name}"]
  key_name = "babu"
  
  tags = {
    Name = "MyWebServer"
  }  
}

output "IP" {
   value = "${aws_instance.my_web_server.public_ip}"
}   
