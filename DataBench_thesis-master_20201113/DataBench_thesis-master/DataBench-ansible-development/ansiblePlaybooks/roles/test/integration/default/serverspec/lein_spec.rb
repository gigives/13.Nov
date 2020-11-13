require 'serverspec'

# Required by serverspec
set :backend, :exec

describe file('/usr/local/bin/lein') do

   it { should exist }

   it { should be_mode 755 }

   it { should contain 'export LEIN_VERSION="2.7.1"' }

end

describe file('/root/.lein/self-installs/leiningen-2.7.1-standalone.jar') do
  it { should exist }
end