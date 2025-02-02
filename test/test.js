const fs = require('fs')
const path = require('path')
const { exec } = require('child_process')
const glob = require('glob')

const VALIDATE = path.resolve(__dirname, '../../verifier-nodejs/validate.js')
const baseDir = path.resolve(__dirname)

const args = process.argv.slice(2)
let pattern = '[0-9]'
if (args.length !== 0) {
  pattern = args[0]
}
const files = glob.sync(`${baseDir}/${pattern}*/*.json`)
files.sort()
files.forEach(file => {
  const logFile = `${file}.log`
  const command = `node ${VALIDATE} ${file}`
  exec(command, (err, stdout, stderr) => {
    if (err) {
      console.error(`Error executing command for ${file}:`, err)
      return
    }
    fs.writeFileSync(logFile, stdout)
    console.log(stdout)
    if (stderr.trim()) {
      console.log(stderr)
    }
  })
})
