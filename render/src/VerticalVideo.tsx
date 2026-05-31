import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type Scene = { src: string; durationInFrames: number; isVideo: boolean };
export type Word = { text: string; start: number; end: number };
export type Props = {
  title: string;
  audio: string;
  fps: number;
  width: number;
  height: number;
  scenes: Scene[];
  captions: { words: Word[] };
};

export const defaultProps: Props = {
  title: "",
  audio: "",
  fps: 25,
  width: 1080,
  height: 1920,
  scenes: [],
  captions: { words: [] },
};

export const totalFrames = (p: Props): number =>
  p.scenes.reduce((a, s) => a + s.durationInFrames, 0);

const resolve = (src: string): string => (src.startsWith("http") ? src : staticFile(src));

const KenBurns: React.FC<{ src: string; durationInFrames: number }> = ({ src, durationInFrames }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.16], { extrapolateRight: "clamp" });
  const ty = interpolate(frame, [0, durationInFrames], [0, -40], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img
        src={resolve(src)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale}) translateY(${ty}px)` }}
      />
    </AbsoluteFill>
  );
};

const Captions: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const current = words.find((w) => t >= w.start && t < w.end);
  if (!current) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 280 }}>
      <div
        style={{
          fontFamily: "'Arial Black', Arial, sans-serif",
          fontSize: 70,
          fontWeight: 900,
          color: "#fff",
          WebkitTextStroke: "7px #000",
          paintOrder: "stroke fill",
          textAlign: "center",
          padding: "0 50px",
          letterSpacing: "-1px",
        }}
      >
        {current.text}
      </div>
    </AbsoluteFill>
  );
};

export const VerticalVideo: React.FC<Props> = ({ audio, scenes, captions }) => {
  let offset = 0;
  const seqs = scenes.map((s, i) => {
    const from = offset;
    offset += s.durationInFrames;
    return (
      <Sequence key={i} from={from} durationInFrames={s.durationInFrames}>
        {s.isVideo ? (
          <OffthreadVideo src={resolve(s.src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <KenBurns src={s.src} durationInFrames={s.durationInFrames} />
        )}
      </Sequence>
    );
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {seqs}
      {audio ? <Audio src={resolve(audio)} /> : null}
      <Captions words={captions.words} />
    </AbsoluteFill>
  );
};
