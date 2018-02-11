module.exports = function (grunt) {
  grunt.initConfig({
    shell: {
      deploy: {
        command: "rsync -rv --exclude 'input_images' --exclude '.git' --exclude 'node_modules' . root@138.197.91.238:/var/www/nicktardif/"
      }
    },

    connect: {
      server: {
        options: {
          keepalive: true,
          port: 8000
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-shell');
  grunt.registerTask('deploy', ['shell:deploy']);
  grunt.registerTask('default', ['connect']);
}
