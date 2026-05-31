import React from "react";
import { Composition } from "remotion";
import { VerticalVideo, defaultProps, totalFrames, Props } from "./VerticalVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="VerticalVideo"
      component={VerticalVideo}
      durationInFrames={Math.max(totalFrames(defaultProps), 1)}
      fps={defaultProps.fps}
      width={defaultProps.width}
      height={defaultProps.height}
      defaultProps={defaultProps}
      calculateMetadata={({ props }: { props: Props }) => ({
        durationInFrames: Math.max(totalFrames(props), props.fps * 2),
        fps: props.fps,
        width: props.width,
        height: props.height,
      })}
    />
  );
};
