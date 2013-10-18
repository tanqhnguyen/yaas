name "app"
description "app setup"
run_list(
  "recipe[app]"
)
default_attributes(
  "build_essential" => {
    "compiletime" => true
  },
  "apt" => {
    "compiletime" => true
  },
  "python" => {
    "install_method"=> "package",
    "prefix_dir"=> "/usr",
    "binary"=> "/usr/bin/python",
    "url"=> "http=>//www.python.org/ftp/python",
    "version"=> "2.7.5",
    "checksum"=> "3b477554864e616a041ee4d7cef9849751770bc7c39adaf78a94ea145c488059",
    "configure_options"=> %W{--prefix=/usr},
    "setuptools_script_url"=> "https://bitbucket.org/pypa/setuptools/raw/0.8/ez_setup.py",
    "pip_script_url"=> "https://raw.github.com/pypa/pip/master/contrib/get-pip.py"
  },
  "app" => {
    "root_dir" => "/vagrant",
    "user" => "vagrant",
    "group" => "vagrant"
  }
) 