import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AdfsLoginService } from '../services/adfsloginservice.service';

@Injectable()
export class LoginSyncGuard implements CanActivate {

  constructor(private adfsLoginService: AdfsLoginService, private router: Router) { }

  canActivate(): Observable<boolean> | Promise<boolean> | boolean {

      if (this.adfsLoginService.userSignedInWithADFSCreds()) {
        return true; // Continue to homepage if user signed in with ADFS creds
      }
      this.router.navigate(['account/loginsync']); // Redirect to the /loginsync page if the user signed in with Login.gov creds
      return false;
  }
}