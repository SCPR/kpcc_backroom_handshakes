'use strict';

const { spawn, exec, execFileSync } = require('child_process');

(function perform(){
  // const proc = spawn('python', ['manage.py', 'election_night']);
  const proc = spawn('./fetch_all.sh');
  // const proc = spawn('fab', ['election_night']);
  proc.on('exit', () => {
    setTimeout(() => {
      perform();
    }, 5 * 60 * 1000);
  });
})()

