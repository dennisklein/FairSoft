# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
#   Spack Project Developers. See the top-level COPYRIGHT file for details.
# Copyright 2020 GSI Helmholtz Centre for Heavy Ion Research GmbH,
#   Darmstadt, Germany
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Fairroot(CMakePackage):
    """C++ simulation, reconstruction and analysis framework for particle physics experiments"""

    homepage = "http://fairroot.gsi.de"
    url = "https://github.com/FairRootGroup/FairRoot/archive/v18.4.0.tar.gz"
    git = "https://github.com/FairRootGroup/FairRoot.git"

    version('develop', branch='dev')
    version('18.4.1', sha256='d8455c4bb705a2d5989ad947ffc50bb2f0d00affb649bb5e30d9463b5be0b490')
    version('18.4.0', sha256='97ad86d039db195acf12e9978eb660daab0c91e95e517921bac5a0f157a3e309')
    version('18.2.1', sha256='a9c22965d2d99e385f64c0df1867b477b9c129bcd087ba3b683d0ada6f3d66d0')

    variant('cxxstd', default='11', values=('11', '14', '17'), multi=False,
            description='Use the specified C++ standard when building.')
    variant('sim', default=True,
            description='Enable simulation engines and event generators')
    variant('examples', default=False,
            description='Install examples')
    variant('pin', default='develop', values=('develop', 'jun19', 'none'), multi=False,
            description='Use certain dependency versions pinned in the given FairSoft release.')

    depends_on('cmake@3.13.4:', type='build')

    depends_on('boost@1.68.0: cxxstd=11 +container')
    depends_on('boost@1.68.0 cxxstd=11 +container', when='pin=jun19')

    depends_on('dds@3.0', when='pin=jun19')

    depends_on('fairlogger@1.4.0:')
    depends_on('fairlogger@1.4.0', when='pin=jun19')

    depends_on('fairmq@1.4.11:')
    depends_on('fairmq@1.4.11', when='pin=jun19')

    depends_on('flatbuffers')

    depends_on('geant4')
    depends_on('geant4@10.5.1~qt~vecgeom~opengl~x11~motif~threads', when='pin=jun19')

    depends_on('googletest@1.7.0:')
    depends_on('googletest@1.8.1', when='pin=jun19')

    depends_on('hepmc@2.06.09 length=CM momentum=GEV', when='pin=jun19')

    depends_on('msgpack-c@3.1:', when='+examples')

    depends_on('protobuf')

    depends_on('pythia6', when='+sim')
    depends_on('pythia6@428-alice1', when='+sim pin=jun19')

    depends_on('pythia8', when='+sim')
    depends_on('pythia8@8240', when='+sim pin=jun19')

    depends_on('root+http', when='pin=none')

    depends_on('fairsoft-config', when='pin=none')

    depends_on('geant3', when='pin=none')

    depends_on('geant4-vmc', when='+sim pin=none')

    _rootspec = {}
    _rootspec['linux']  = 'root@6.16.00+fortran+gdml+memstat+pythia6+pythia8+vc~vdt+python+tmva+xrootd+sqlite ^mesa~llvm'
    _rootspec['darwin'] = 'root@6.16.00+fortran+gdml+memstat+pythia6+pythia8+vc~vdt+python+tmva+xrootd+sqlite+aqua'
    for platform in ['linux', 'darwin']:
        depends_on(_rootspec[platform], when='pin=jun19 platform={}'.format(platform))

        depends_on('fairsoft-config@jun19 ^{}'.format(_rootspec[platform]), when='pin=jun19 platform={}'.format(platform))

        depends_on('geant3@2.7 ^{}'.format(_rootspec[platform]), when='pin=jun19 platform={}'.format(platform))

        depends_on('geant4-vmc@4-0-p1 ^{}'.format(_rootspec[platform]), when='+sim pin=jun19 platform={}'.format(platform))

    depends_on('vgm', when='+sim')
    depends_on('vgm@4-5', when='+sim pin=jun19')

    depends_on('vmc', when='@18.4: ^root@6.18:')

    depends_on('yaml-cpp', when='@18.2:')

    ### jun19 concretizer hints
    depends_on('python@2.7.18', when='pin=jun19')
    depends_on('py-numpy@1.16.6', when='pin=jun19')
    depends_on('py-setuptools@44.1.0', when='pin=jun19')

    patch('cmake_utf8.patch', when='@18.2.1')
    patch('fairlogger_incdir.patch', level=0, when='@18.2.1')
    patch('find_pythia8_cmake.patch', when='@:18.4.0 +sim')
    patch('support_geant4_with_external_clhep_18.2.patch', when='@18.2 +sim')
    patch('support_geant4_with_external_clhep.patch', when='@18.4 +sim ^Geant4@:10.5')

    def setup_build_environment(self, env):
        super(Fairroot, self).setup_build_environment(env)
        if self.spec.satisfies('@:18,develop'):
            env.append_flags('CXXFLAGS',
                '-std=c++%s' % self.spec.variants['cxxstd'].value)
        env.unset('SIMPATH')
        env.unset('FAIRSOFT_ROOT')

    def cmake_args(self):
        options = []
        if self.spec.satisfies('@:18,develop'):
            options.append('-DROOTSYS={0}'.format(self.spec['root'].prefix))
            options.append('-DPYTHIA8_DIR={0}'.format(
                self.spec['pythia8'].prefix))

        options.append('-DBUILD_EXAMPLES:BOOL=%s' %
                       ('ON' if '+examples' in self.spec else 'OFF'))

        if self.spec.satisfies('^boost@:1.69.99'):
            options.append('-DBoost_NO_BOOST_CMAKE=ON')

        return options

    def common_env_setup(self, env):
        # So that root finds the shared library / rootmap
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)

    def setup_run_environment(self, env):
        self.common_env_setup(env)

    def setup_dependent_build_environment(self, env, dependent_spec):
        self.common_env_setup(env)

    def setup_dependent_run_environment(self, env, dependent_spec):
        self.common_env_setup(env)
