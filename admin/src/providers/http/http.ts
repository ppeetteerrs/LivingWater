import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable } from "@angular/core";

import "rxjs";
import { searchResults, VerseRecord } from "./response_interface";
import { Observable } from "rxjs/Observable";

@Injectable()
export class HttpProvider {
  //base_url: string = "http://dictionary-keywords-test-ppeetteerrs.c9users.io:8080";
  // base_url: string = "http://localhost:9001";
  base_url: string = "http://128.199.234.238:8080";

  constructor(public http: HttpClient) { }

  searchRankings(sentence: string): Observable<searchResults> {
    let params = new HttpParams().set("sentence", sentence);
    return this.http.get<searchResults>(this.base_url + "/get_rankings", {
      params
    });
  }

  searchVerse(query_string: string): Observable<VerseRecord> {
    let params = new HttpParams().set("query_string", query_string);
    return this.http.get<VerseRecord>(this.base_url + "/search_verse", {
      params
    });
  }

  editKeywordLink(
    verse_location: string,
    word: string,
    level: number,
    delete_item: boolean
  ): Observable<any> {
    let json_string = {
      location: verse_location,
      word: word,
      level: level,
      delete: delete_item
    };
    let params = new HttpParams().set(
      "json_string",
      JSON.stringify(json_string)
    );
    return this.http.get(this.base_url + "/edit_link", {
      params
    });
  }

  editVerseLocation(
    old_location: string,
    new_location: string
  ): Observable<VerseRecord> {
    let params = new HttpParams()
      .set("old_location", old_location)
      .set("new_location", new_location);
    return this.http.get<VerseRecord>(this.base_url + "/update_verse", {
      params
    });
  }

  addVerse(
    location: string,
    lvl1: string[],
    lvl2: string[],
    lvl3: string[]
  ): Observable<VerseRecord> {
    let json_object = {
      location: location,
      lvl1: lvl1,
      lvl2: lvl2,
      lvl3: lvl3
    };
    let params = new HttpParams().set(
      "json_string",
      JSON.stringify(json_object)
    );
    return this.http.get<VerseRecord>(this.base_url + "/add_verse", {
      params
    });
  }

  removeVerse(location: string): Observable<VerseRecord> {
    let params = new HttpParams().set("location", location);
    return this.http.get<VerseRecord>(this.base_url + "/remove_verse", {
      params
    });
  }

  getSynonyms(word: string): Observable<any> {
    let params = new HttpParams().set("base_word", JSON.stringify(word));
    return this.http.get(this.base_url + "/get_synonyms", {
      params
    });
  }

  modifySynonyms(json_string: string): Observable<any> {
    let params = new HttpParams().set("json_string", json_string);
    return this.http.get(this.base_url + "/modify_synonyms", {
      params
    });
  }

  modifyRelatedWords(json_string: string): Observable<any> {
    let params = new HttpParams().set("json_string", json_string);
    return this.http.get(this.base_url + "/modify_related_words", {
      params
    });
  }


  addWord(new_word: string, copy_from: string): Observable<any> {
    let params = new HttpParams().set("new_word", new_word).set("copy", copy_from);
    return this.http.get(this.base_url + "/add_word", {
      params
    });
  }


  deleteWord(word: string): Observable<any> {
    let params = new HttpParams().set("word", word);
    return this.http.get(this.base_url + "/delete_word", {
      params
    });
  }
}
