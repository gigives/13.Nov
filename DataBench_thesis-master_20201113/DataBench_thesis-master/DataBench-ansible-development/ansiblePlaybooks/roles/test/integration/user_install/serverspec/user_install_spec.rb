require 'serverspec'

# Required by serverspec
set :backend, :exec

describe file('/home/myuser/.lein/self-installs/leiningen-2.7.1-standalone.jar') do
  it { should exist }
end