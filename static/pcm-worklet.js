// Converts mic audio (usually 48 kHz float) to 16 kHz signed 16-bit mono PCM
// and posts exactly 1024-byte frames (512 samples = 32 ms), the format Gnani
// Prisma's realtime API requires.
class PCM16Downsampler extends AudioWorkletProcessor {
  constructor() {
    super();
    this.ratio = sampleRate / 16000; // `sampleRate` is a global in the worklet scope
    this.buf = [];
    this.pos = 0;
    this.out = new Int16Array(512);
    this.n = 0;
  }

  process(inputs) {
    const ch = inputs[0] && inputs[0][0];
    if (!ch) return true;
    for (let i = 0; i < ch.length; i++) this.buf.push(ch[i]);

    while (this.buf.length - this.pos >= Math.max(this.ratio, 1)) {
      // Average the input samples covered by one output sample (a simple low-pass).
      const start = Math.floor(this.pos);
      const end = Math.max(start + 1, Math.floor(this.pos + this.ratio));
      let s = 0;
      for (let k = start; k < end; k++) s += this.buf[k];
      s = Math.max(-1, Math.min(1, s / (end - start)));
      this.out[this.n++] = s < 0 ? s * 0x8000 : s * 0x7fff;
      if (this.n === 512) {
        this.port.postMessage(this.out.buffer.slice(0));
        this.n = 0;
      }
      this.pos += this.ratio;
    }
    const drop = Math.floor(this.pos);
    if (drop > 0) {
      this.buf.splice(0, drop);
      this.pos -= drop;
    }
    return true;
  }
}

registerProcessor("pcm16-downsampler", PCM16Downsampler);
