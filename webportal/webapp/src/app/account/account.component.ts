import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CognitoService } from '../../services/cognito.service';
import { ApiGatewayService } from '../../services/apigateway.service';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.css']
})
export class AccountComponent implements OnInit {

  constructor(
    private cognitoService: CognitoService,
    private gatewayService: ApiGatewayService,
    private router: Router
  ) { }

  ngOnInit() {
    this.getUserInfo();
  }

  getUserInfo() {
    this.gatewayService.getUserInfo('user').subscribe(
        (response: any) => {
            sessionStorage.setItem('username', response.username);
            sessionStorage.setItem('email', response.email);
            sessionStorage.setItem('stacks', JSON.stringify(response.stacks));
            sessionStorage.setItem('datasets', JSON.stringify(response.datasets));
            sessionStorage.setItem('roles', response.role);

            for (var i = 0; i < response.stacks.length; i++) {
              if (response.stacks[i].instance_id) {
                sessionStorage.setItem('instance-id', response.stacks[i].instance_id);
                sessionStorage.setItem('team_bucket_name', response.stacks[i].team_bucket_name);
              }
            }
        }
    );
}

  userLogout() {
    this.cognitoService.logout();
    localStorage.clear();
    sessionStorage.clear();
    this.router.navigate(['/']);
  }
}