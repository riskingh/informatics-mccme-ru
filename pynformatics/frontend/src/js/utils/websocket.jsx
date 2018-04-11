import io from 'socket.io-client';


export default class Socket {
  constructor(url, dispatch) {
    this.dispatch = dispatch;
    this.socket = io(url, { transports: ['websocket', 'polling'] });

    this.socket.on('connect', () => this.onConnect());
    this.socket.on('disconnect', () => this.onDisconnect());
    this.socket.on('RUNS_FETCH', data => this.onRunsFetch(data));
    this.socket.on('SUBMIT_ERROR', data => this.onSubmitError(data));
    this.socket.on('SUBMIT_SUCCESS', data => this.onSubmitSuccess(data));
  }

  onConnect() {}
  onDisconnect() {}

  onRunsFetch(data) {}
  onSubmitError(data) {}
  onSubmitSuccess(data) {}

  // onMessage(event) {
  //   this.dispatch({
  //     type: 'WEBSOCKET_MESSAGE',
  //     data: JSON.parse(event.data),
  //   })
  // }
}
