import {Injectable} from '@angular/core';
import {Http} from '@angular/http';
import 'rxjs/add/operator/map';
import {OCCASIONS_DATA} from './occasions_data';
import {TOPICS_DATA} from './topics_data';

@Injectable()
export class LocalVersesProvider {
  topics_data = TOPICS_DATA;
  occasions_data = OCCASIONS_DATA;

  constructor(public http: Http) {}

  localSearch(
    search_input: string,
    arr: any[],
    field: string = null,
    sort: boolean = true
  ) {
    if (field == null) {
      let filtered_arr = arr.filter((item, index, arr) => {
        return item.toLowerCase().indexOf(search_input.toLowerCase()) > -1;
      });
      if (sort) {
        filtered_arr = filtered_arr.sort((itema, itemb) => {
          return (
            itema.toLowerCase().indexOf(search_input.toLowerCase()) -
            itemb.toLowerCase().indexOf(search_input.toLowerCase())
          );
        });
      }
      return filtered_arr;
    } else {
      let filtered_arr = arr.filter((item, index, arr) => {
        return (
          item[field].toLowerCase().indexOf(search_input.toLowerCase()) > -1
        );
      });
      if (sort) {
        filtered_arr = filtered_arr.sort((itema, itemb) => {
          return (
            itema[field].toLowerCase().indexOf(search_input.toLowerCase()) -
            itemb[field].toLowerCase().indexOf(search_input.toLowerCase())
          );
        });
      }
      return filtered_arr;
    }
  }
}
