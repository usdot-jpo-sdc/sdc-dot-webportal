import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-loginsync',
  templateUrl: './loginsync.component.html',
  styleUrls: ['./loginsync.component.css',
              '../../../../../node_modules/uswds/src/stylesheets/uswds.scss']
})
export class LoginSyncComponent implements OnInit {
  username: string;
  password: string;

  constructor() { }

  ngOnInit() {
  }

  onSubmit() {
    console.log(`User tried to sign in with creds: ${this.username}, ${this.password}`);
  }

}