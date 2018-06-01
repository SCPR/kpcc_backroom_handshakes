'use strict';

const { spawn, exec, execFileSync } = require('child_process');

(function perform(){
  const proc = spawn('fab', ['election_night']);
  proc.on('exit', () => {
    setTimeout(() => {
      perform();
    }, 10 * 60 * 1000);
  });
})()

