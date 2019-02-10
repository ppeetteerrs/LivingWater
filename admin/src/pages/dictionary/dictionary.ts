import { Component } from "@angular/core";
import {
  IonicPage,
  NavController,
  NavParams,
  ToastController,
  AlertController,
  LoadingController
} from "ionic-angular";
import { HttpProvider } from "../../providers/http/http";

@IonicPage()
@Component({
  selector: "page-dictionary",
  templateUrl: "dictionary.html"
})
export class DictionaryPage {
  input_word: string = "";

  current_word: string = "";

  synonyms: any[] = [];

  constructor(
    public navCtrl: NavController,
    public navParams: NavParams,
    public loadingCtrl: LoadingController,
    public http: HttpProvider,
    public alertCtrl: AlertController,
    public toastCtrl: ToastController
  ) { }

  presentToast(message: string) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 7000
    });
    toast.present();
  }

  async search(word: string, load: boolean = true, loader) {
    this.synonyms = [];

    if (word == "") {
      this.presentToast("Please don't make it crash =)");
      return false;
    }

    let loading;
    if (load) {
      loading = this.loadingCtrl.create({
        content: "Please wait..."
      });
      loading.present();
    }
    this.current_word = word;

    this.http.getSynonyms(word).subscribe(
      response => {
        let level3 = response.filter((item, index, arr) => {
          return item[1].parent == null && item[1].weight == 1;
        }).sort((item1, item2) => {
          return item1[0].localeCompare(item2[0]);
        });
        let level2 = response.filter((item, index, arr) => {
          return item[1].parent == null && item[1].weight == 2 / 3;
        }).sort((item1, item2) => {
          return item1[0].localeCompare(item2[0]);
        });
        let related_words = response.filter((item, index, arr) => {
          return item[1].parent != null;
        }).sort((item1, item2) => {
          return item1[0].localeCompare(item2[0]);
        });
        let level1 = response.filter((item, index, arr) => {
          return item[1].parent == null && item[1].weight == 1 / 3;
        }).sort((item1, item2) => {
          return item1[0].localeCompare(item2[0]);
        });
        this.synonyms = [level3, level2, level1, related_words];
        this.presentToast(
          "Found " + response.length + " synonyms for " + this.current_word
        );
        console.log(this.synonyms);
        if (load) {
          loading.dismiss();
        } else {
          loader.dismiss();
        }
      },
      err => {
        if (load) {
          loading.dismiss();
        } else {
          loader.dismiss();
        }
        this.presentToast(err.error);
      }
    );
  }

  addSynonym(level) {
    level = parseInt(level);
    const alert = this.alertCtrl.create({
      title: "Add Level " + level + " Synonym for " + this.current_word,
      inputs: [
        {
          name: "new_synonym",
          placeholder: "New Synonym"
        }
      ],
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.modifySynonymToCloud(
              this.current_word,
              data.new_synonym,
              level,
              true
            );
          }
        }
      ]
    });
    alert.present();
  }

  addWord() {
    const alert = this.alertCtrl.create({
      title: "Add new word to dictionary",
      inputs: [
        {
          name: "new_word",
          placeholder: "New Word"
        },
        {
          name: "copy",
          placeholder: "Copy from? (Optional)"
        }
      ],
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.addWordToCloud(
              data.new_word,
              data.copy
            );
          }
        }
      ]
    });
    alert.present();
  }


  deleteWord() {
    const alert = this.alertCtrl.create({
      title: "Do you want to delete " + this.current_word + " from the dictionary?",
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.deleteWordFromCloud();
          }
        }
      ]
    });
    alert.present();
  }

  removeSynonym(synonym_to_remove: string) {
    const alert = this.alertCtrl.create({
      title: "Are you sure?",
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.modifySynonymToCloud(
              this.current_word,
              synonym_to_remove,
              -1,
              false
            );
          }
        }
      ]
    });
    alert.present();
  }

  modifySynonymToCloud(
    base_word: string,
    new_synonym: string,
    level: number,
    add_syn: boolean
  ) {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loading.present();
    let json_string = {
      base_word: base_word,
      synonym: new_synonym,
      level: level,
      add_syn: add_syn
    };
    this.http.modifySynonyms(JSON.stringify(json_string)).subscribe(
      response => {
        this.search(this.current_word, false, loading);
      },
      err => {
        loading.dismiss();
        this.presentToast(err.error);
      }
    );
  }

  addWordToCloud(
    new_word: string,
    copy_from: string
  ) {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loading.present();
    this.http.addWord(new_word, copy_from).subscribe(
      response => {
        this.search(new_word, false, loading);
      },
      err => {
        loading.dismiss();
        this.presentToast(err.error);
      }
    );
  }

  deleteWordFromCloud() {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loading.present();
    this.http.deleteWord(this.current_word).subscribe(
      response => {
        this.search(this.current_word, false, loading);
      },
      err => {
        loading.dismiss();
        this.presentToast(err.error);
      }
    );
  }

  addRelation() {
    const alert = this.alertCtrl.create({
      title: "Add Relationship for " + this.current_word,
      inputs: [
        {
          name: "new_related_word",
          placeholder: "New Related Word"
        }
      ],
      buttons: [

        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.modifyRelatedWordToCloud(
              this.current_word,
              data.new_related_word,
              true
            );
          }
        }
      ]
    });
    alert.present();
  }

  removeRelation(related_word_to_remove: string) {
    const alert = this.alertCtrl.create({
      title: "Are you sure?",
      buttons: [

        {
          text: "Cancel",
          role: "cancel",
          handler: data => { }
        },
        {
          text: "Confirm",
          handler: data => {
            this.modifyRelatedWordToCloud(
              this.current_word,
              related_word_to_remove,
              false
            );
          }
        }
      ]
    });
    alert.present();
  }

  modifyRelatedWordToCloud(
    base_word: string,
    new_related_word: string,
    add_link: boolean
  ) {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loading.present();
    let json_string = {
      base_word: base_word,
      related_word: new_related_word,
      add_link: add_link
    };
    this.http.modifyRelatedWords(JSON.stringify(json_string)).subscribe(
      response => {
        this.search(this.current_word, false, loading);
      },
      err => {
        loading.dismiss();
        this.presentToast(err.error);
      }
    );
  }
}
