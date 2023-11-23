#include "FastLED.h"

#define LED_COUNT 120
#define LED_DT 2 /* data pin */

#define MAX_BUFFER_SIZE 481 /* bytes */
#define BLINK_PERIOD 1000   /* ms */
#define BLINK_TIMEOUT 2000  /* ms */
#define BRIGHTNESS 255      /* 0 - 255 */
#define MAX_BRIGHTNESS 30   /* 0 - 255 */
#define BAUD_RATE 115200    /* bps */

struct CRGB leds[LED_COUNT];

void setup() {
  // For convenient connection
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);

  Serial.begin(BAUD_RATE);
  Serial.setTimeout(5);

  FastLED.setBrightness(BRIGHTNESS);
  FastLED.addLeds<WS2812B, LED_DT, GRB>(leds, LED_COUNT);
  FastLED.show();
}

void set_all(int r, int g, int b) {
  for (int i = 0; i < LED_COUNT; i++) leds[i].setRGB(r, g, b);

  FastLED.show();
}

bool blinkState = 0;
unsigned long lastSignal = 0;
unsigned long blinkTimer = 0;

void loop() {
  if (Serial.available()) {
    char first = Serial.read();
    if (first == '{') {
      lastSignal = millis();

      char data[MAX_BUFFER_SIZE];
      int amount = Serial.readBytesUntil('}', data, MAX_BUFFER_SIZE);
      data[amount] = NULL;

      char* offset = data;
      int i = 0;

      do {
        int brt = atoi(offset);
        brt = constrain(brt, 0, MAX_BRIGHTNESS);

        leds[i++].setRGB(brt, map(brt, 0, 255, 0, 50), brt);

        offset = strchr(offset, '|');
      } while (offset++);

      FastLED.show();
    }
  } else {
    if (millis() - lastSignal <= BLINK_TIMEOUT) return;
    if (millis() - blinkTimer <= BLINK_PERIOD) return;
    set_all(0, 0, 0);
    blinkTimer = millis();
    leds[0].setRGB(0, 0, blinkState ? 2 : 0);
    blinkState ^= 1;
    FastLED.show();
  }
}
