#include <FastLED.h>

#define LED_DT 2             /* data pin */
#define LED_COUNT 120        /* Full count of strip leds */
#define BRIGHTNESS_SCALE 255 /* 0 - 255 */
#define MAX_BRIGHTNESS 30    /* 0 - 255 */
#define BLINK_PERIOD 1000    /* (ms) For blink when not connected */
#define BLINK_TIMEOUT 2000   /* (ms) Wait time before blink */
#define MAX_BUFFER_SIZE 361  /* (bytes) Serial buffer size; default is 361*/
                             /* (LED_COUNT*3 + LED_COUNT-1 + 2)    */
#define BAUD_RATE 115200     /* bps */

#define MSG_START '['
#define MSG_END ']'
#define MSG_SEP ','

struct CRGB leds[LED_COUNT];

void setup() {
  // For convenient connection (NANO)
  // x GND
  // x D2 (data)
  // x D3 (5v)
  pinMode(3, OUTPUT);
  digitalWrite(3, HIGH);

  Serial.begin(BAUD_RATE);
  Serial.setTimeout(5);

  FastLED.setBrightness(BRIGHTNESS_SCALE);
  FastLED.addLeds<WS2812B, LED_DT, GRB>(leds, LED_COUNT);
  FastLED.show();
}

void set_all(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < LED_COUNT; i++) leds[i].setRGB(r, g, b);

  FastLED.show();
}

bool blinkState = 0;
unsigned long lastSignal = 0;
unsigned long blinkTimer = 0;

void loop() {
  if (Serial.available()) {
    char first = Serial.read();
    if (first == MSG_START) {
      lastSignal = millis();

      char data[MAX_BUFFER_SIZE];
      int amount = Serial.readBytesUntil(MSG_END, data, MAX_BUFFER_SIZE);
      data[amount] = NULL;

      char *offset = data;
      int i = 0;

      do {
        // uint8_t brt = atoi(offset);
        uint8_t brt = strtoul(offset, NULL, 16);
        brt = constrain(brt, 0, MAX_BRIGHTNESS);

        leds[i++].setRGB(brt, map(brt, 0, 255, 0, 50), brt);  // Pink :3

        offset = strchr(offset, MSG_SEP);
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
