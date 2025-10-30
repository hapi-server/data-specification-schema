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
    if (err && stderr.trim()) {
      // If validation fails, validate.js exits with code 1 and no stderr.
      // If stderr exists, it's an execution error.
      console.error(`Error executing command for ${file}:`, err)
      return
    }
    fs.writeFileSync(logFile, stdout)

    if (typeof stdout === 'string') {

      const RED = '\x1b[41m'
      const RESET = '\x1b[0m'
      stdout = stdout.replace(/✗/g, `${RED}✗${RESET}`)
      const GREEN = '\x1b[42m'
      stdout = stdout.replace(/✓/g, `${GREEN}✓${RESET}`)
      const YELLOW = '\x1b[43m'
      stdout = stdout.replace(/⚠/g, `${YELLOW}⚠${RESET}`)
    }
    console.log(stdout)
    if (stderr.trim()) {
      console.log(stderr)
    }
  })
})
