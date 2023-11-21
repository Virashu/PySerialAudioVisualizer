#include "FastLED.h"

#define LED_COUNT 120
#define LED_DT 2 /* data pin */

#define MAX_BUFFER_SIZE 481 /* bytes */
#define BLINK_PERIOD 1000   /* ms */
#define BLINK_TIMEOUT 2000  /* ms */
#define BRIGHTNESS 255      /* 0 - 255 */
#define MAX_BRIGHTNESS 30   /* 0 - 255 */

struct CRGB leds[LED_COUNT];

void setup() {
  // For convenient connection
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);

  Serial.begin(115200);
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
    set_all(0, 0, 0);
    if (millis() - blinkTimer > BLINK_PERIOD) {
      blinkTimer = millis();
      leds[0].setRGB(0, 0, blinkState ? 2 : 0);
      blinkState ^= 1;
    }
    FastLED.show();
  }
}

String getValue(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}