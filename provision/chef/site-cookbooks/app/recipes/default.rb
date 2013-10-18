#
# Cookbook Name:: app
# Recipe:: default
#
# Copyright 2013, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
include_recipe "apt"
include_recipe "build-essential"
include_recipe "python"

packages = "sqlite3 gettext"
packages.split(" ").each do |p|
  package p
end

python_virtualenv "#{node["app"]["root_dir"]}/.env" do
  owner node["app"]["user"]
  group node["app"]["group"]
  action :create
end

python_pip "django" do
  virtualenv "#{node["app"]["root_dir"]}/.env"
end