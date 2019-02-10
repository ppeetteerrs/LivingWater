import inquirer from 'inquirer';
import shell from 'shelljs';
import fs from 'fs';
import colors from 'colors';
import xmljs from 'xml-js';

colors.setTheme({
  silly: 'rainbow',
  input: 'grey',
  verbose: 'grey',
  prompt: 'grey',
  info: 'cyan',
  data: 'magenta',
  help: 'cyan',
  warn: 'yellow',
  debug: 'blue',
  error: 'red'
});

const ANDROID_BUILD_PATH = 'platforms/android/app/build/outputs/apk/release/';

async function deploy() {
  const oldPackageJSON = JSON.parse(fs.readFileSync(`${__dirname}/package.json`));
  const configXML = xmljs.xml2js(fs.readFileSync(`${__dirname}/config.xml`), {
    compact: true
  });


  const platformChoices = ['iOS', 'Android'];
  const updateChoices = ['Major', 'Minor', 'Patch', 'None'];

  const {platform, updateType, commitMessage} = await inquirer.prompt([
    {
      type: 'list',
      name: 'platform',
      message: 'Which Platform to Deploy To?',
      choices: platformChoices,
      default: platformChoices[0]
    },
    {
      type: 'list',
      name: 'updateType',
      message: 'Major / Minor / Patch / No Update?',
      choices: updateChoices,
      default: updateChoices[3]
    }, {
      type: 'input',
      name: 'commitMessage',
      message: 'Git Commit Message',
      default: ''
    }
  ]);
  const newVersion = updateBuildVersion(oldPackageJSON.version, updateType);
  const newPackageJSON = {
    ...oldPackageJSON,
    version: newVersion
  };
  configXML.widget._attributes.version = newVersion;
  fs.writeFileSync(`${__dirname}/package.json`, JSON.stringify(newPackageJSON, null, 4));
  fs.writeFileSync(`${__dirname}/config.xml`, xmljs.js2xml(configXML, {
    compact: true,
    spaces: 2
  }));
  gitCommit(newVersion, commitMessage);
  build(platform, newVersion);
}

function updateBuildVersion(oldVersion, updateType) {
  const oldVersionArray = oldVersion.split('.');
  switch (updateType) {
    case 'Major':
      oldVersionArray[0] = (parseInt(oldVersionArray[0], 10) + 1).toString();
      oldVersionArray[2] = '0';
      oldVersionArray[2] = '0';
      break;
    case 'Minor':
      oldVersionArray[1] = (parseInt(oldVersionArray[1], 10) + 1).toString();
      oldVersionArray[2] = '0';
      break;
    case 'Patch':
      oldVersionArray[2] = (parseInt(oldVersionArray[2], 10) + 1).toString();
      break;
    default:
      break;
  }
  const newVersion = oldVersionArray.join('.');
  console.log(`[DEPLOY] Updating from Version ${oldVersion} -> ${newVersion}...\n`.info.bold);
  return newVersion;
}

function gitCommit(version, message) {
  console.log('[DEPLOY] Updating Git...'.info.bold);
  shell.exec('git add -A');
  shell.exec(`git commit -m "V${version} - ${message}"`);
  shell.exec(`git tag -f ${version}`);
  shell.exec('git push origin master --tags');
  shell.exec('git push ionic master');
}

function build(platform, version) {
  console.log('[DEPLOY] Generating Icons and Splash Screens...'.info.bold);
  shell.exec(`cp resources/icon_${platform.toLowerCase()}.png resources/icon.png`);
  shell.exec('ionic cordova resources --force');
  switch (platform) {
    case 'iOS':
      buildIOS(version);
      break;
    default:
      buildAndroid(version);
      break;
  }
}

function buildAndroid(version) {
  console.log('[DEPLOY] Building APK'.info.bold);
  shell.exec('ionic cordova build android --prod --release');
  console.log('[DEPLOY] Signing APK'.info.bold);
  shell.exec(`jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore fastlane/secret/livingwater.keystore ${ANDROID_BUILD_PATH}app-release-unsigned.apk livingwater -storepass livingwater -keypass livingwater`);
  shell.exec(`~/Library/Android/sdk/build-tools/28.0.1/zipalign -v 4 ${ANDROID_BUILD_PATH}app-release-unsigned.apk ${ANDROID_BUILD_PATH}LivingWaterV${version}.apk`);
  console.log('[DEPLOY] Handing Over to Fastlane'.info.bold);
  shell.exec(`cp ${ANDROID_BUILD_PATH}LivingWaterV${version}.apk build/android_output.apk`);
  shell.exec('fastlane android alpha');
}

function buildIOS() {
  console.log('[DEPLOY] Building XCode Project'.info.bold);
  shell.exec('ionic cordova build ios --prod --release');
  console.log('[DEPLOY] Handing Over to Fastlane'.info.bold);
  shell.exec('fastlane ios beta');
}

deploy();

