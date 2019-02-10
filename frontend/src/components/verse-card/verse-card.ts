import { Component, Input } from '@angular/core';

@Component({
  selector: 'verse-card',
  templateUrl: 'verse-card.html'
})
export class VerseCardComponent {
  @Input("verse-item") verseItem;

  constructor() {
  }

}

/*
<ion-card class="result-card">
    <ion-row class="result-row header">
      <ion-col col-2 class="result-col">
        <div class="result-container">
          <h1 class="result-ranking">{{verseItem.ranking}}</h1>
        </div>
      </ion-col>
      <ion-col col-8 class="result-col">
        <p class="result-location">{{verseItem.verse_location}}</p>
      </ion-col>
      <ion-col col-1 class="result-col">
        <div class="result-container">
          <ion-icon name="star-outline" class="action-buttons"></ion-icon>
        </div>
      </ion-col>
      <ion-col col-1 class="result-col">
          <button ion-button icon-only clear color="dark" (click)="copyVerse(verseItem)">
            <ion-icon name="copy"></ion-icon>
          </button>
      </ion-col>
    </ion-row>
    <ion-row class="result-row">
      <ion-col col-12 class="result-col">
        <div class="result-text">
          <i>{{verseItem.verse_text}}</i>
        </div>
      </ion-col>
    </ion-row>

  </ion-card>
*/
