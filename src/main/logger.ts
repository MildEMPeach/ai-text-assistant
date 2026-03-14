import log from 'electron-log/main';

log.initialize();
log.transports.file.level = 'info';
log.transports.console.level = 'info';

export default log;
