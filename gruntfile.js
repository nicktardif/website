module.exports = function (grunt) {
  grunt.initConfig({
    shell: {
      deploy: {
        command: "rsync -rv --progress --exclude 'input_images' --exclude '*.png' --exclude '.git' --exclude 'node_modules' . nick-website:/var/www/nicktardif/"
      }
    },

    connect: {
      server: {
        options: {
          keepalive: true,
          port: 8000
        }
      }
    },

    cssmin: {
      target: {
        files: {
          'css/nicktardif.min.css': ['css/*.css', '!css/*.min.css']
        }
      }
    },

    uglify: {
      target: {
        files: {
          'js/nicktardif.min.js': ['js/main.js', 'js/photoswipe.min.js', 'js/photoswipe-ui-default.min.js', 'js/webfont.min.js']
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-shell');
  grunt.registerTask('deploy', ['shell:deploy']);
  grunt.registerTask('default', ['connect']);
  grunt.registerTask('build', ['cssmin', 'uglify']);
}
