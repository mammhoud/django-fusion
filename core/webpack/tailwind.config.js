/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.{html,js}"],
  prefix: 'tw-',
  theme: {
    extend: {
      fontFamily: {
        "body-font": ["Plus Jakarta Sans", "sans-serif"],
        awesome: "Font Awesome 5 Free",
      },
      fontWeight: {
        inherit: "inherit",
      },
      colors: {
        "main-color": "var(--main-color)",
        "heading-color": "#101A29",
        "paragraph-color": "#737588",
        "border-color": "#bdbecc",
      },
      keyframes: {
        topImageBounce: {
          "0%": { transform: "translateY(-8px)" },
          "50%": { transform: "translateY(12px)" },
          "100%": { transform: "translateY(-8px)" },
        },
        leftImageBounce: {
          "0%": { transform: "translateX(-5px)" },
          "50%": { transform: "translateX(10px)" },
          "100%": { transform: "translateX(-5px)" },
        },
        spin: {
          "0%": {
            transform: "rotate(0deg)",
            "transform-origin": "50%",
          },
          "100%": {
            transform: "rotate(360deg)",
            "transform-origin": "50%",
          },
        },
        ripple: {
          "0%": {
            "box-shadow":
              "0 0 0 0 rgba(255, 255, 255, 0.1), 0 0 0 10px rgba(255, 255, 255, 0.1), 0 0 0 20px rgba(255, 255, 255, 0.1)",
          },
          "100%": {
            "box-shadow":
              "0 0 0 10px rgba(255, 255, 255, 0.1), 0 0 0 20px rgba(255, 255, 255, 0.1), 0 0 0 100px rgba(255, 255, 255, 0)",
          },
        },
        backtoTopBounce: {
          "0%": { transform: "translateY(-5px)" },
          "50%": { transform: "translateY(10px)" },
          "100%": { transform: "translateY(-5px)" },
        },
        skRotate: {
          "0%": {
            transform: "rotate(0deg)",
          },
          "100%": {
            transform: "rotate(360deg)",
          },
        },
        skBounce: {
          "0%, 100%": {
            transform: "scale(0)",
          },
          "50%": {
            transform: "scale(1)",
          },
        },
        "right-image-bounce": {
          "0%": { transform: "translateX(-5px)" },
          "50%": { transform: "translateX(10px)" },
          "100%": { transform: "translateX(-5px)" },
        },
        move: {
          "0%": { transform: "translateX(0px)" },
          "50%": { transform: "translateX(20px)" },
          "100%": { transform: "translateX(0px)" },
        },
      },
      animation: {
        topImageBounce: "topImageBounce 3s infinite ease-in-out",
        leftImageBounce: "leftImageBounce 3s infinite ease-in-out",
        spin: "spin 3s infinite ease-in-out",
        ripple: "ripple 2.5s linear infinite",
        backtoTopBounce: "backtoTopBounce 4s infinite ease-in-out",
        skRotate: "skRotate 2.0s infinite linear",
        skBounce: "skBounce 2.0s infinite ease-in-out",
        move: "move 6s ease-in-out infinite",
        moveTwo: "move 4s ease-in-out infinite",
        "right-image-bounce": "right-image-bounce 3s infinite ease-in-out",
      },
      backgroundImage: {
        "grd-one": "linear-gradient(to left, #f8f9fc 50%, transparent)",
        "grd-gray": "linear-gradient(#F8F9FC, #D9E5FF)",
        "grd-two": "linear-gradient(to right, #F8F9FC 50%, transparent)",
        "grd-three": "linear-gradient(to right, #F99746, #EE0020)",
        "grd-four": "linear-gradient(56.64deg, #2600fc 0.04%, #ff00ea 99.88%)",
        "grd-five": "linear-gradient(56.64deg, #ff00ea 0.04%, #2600fc 99.88%)",
        "grd-six": "linear-gradient(56.64deg, #2600fc 0.04%, #6d18ef 99.88%)",
        "grd-eight": "linear-gradient(56.64deg, #6d18ef 0.04%, #2600fc 99.88%)",
        "grd-nine":
          "linear-gradient(90deg, #FFB545 2.18%, rgba(255,181,69,0.00) 99.77%)",
        "grd-ten":
          "linear-gradient(90deg, #625FFB 2.18%, rgba(98,95,251,0.00) 99.77%)",
        "grd-eleven":
          "linear-gradient(180deg, rgba(241,243,253,0.00) 0%, #F1F3FD 100%)",
        "custom-gradient":
          "radial-gradient(circle closest-side, #050231 0, #050231 43.68%, transparent 43.68%, transparent 84%, #050231 0), conic-gradient(from 42deg, #00D199 0, #00D199 49.4%, #C87B07 0, #C87B07 79.3%, #A92535 0, #A92535 100%)",
      },
      boxShadow: {
        sm: "0px 3px 20px rgba(0, 33, 71, 0.06)",
        md: "0px 10px 30px rgba(0, 33, 71, 0.08)",
        lg: "0px 10px 60px rgba(0, 0, 0, 0.07)",
        xl: "0 0 5px rgba(0, 0, 0, 0.1)",
        xxl: "0 4px 15px rgba(19, 16, 34, 0.1)",
        "2xl": "0px 8px 30px rgb(0 0 0 / 10%)",
        "3xl": "0 4.4px 30px rgba(19, 16, 34, 0.05)",
        "4xl": "0 0 15px 0 rgba(#000,.05)",
        "5xl": "0px 4.8px 20px rgba(19, 16, 34, 0.1)",
        "6xl": "0 0 2px 2px rgba(0, 0, 0, 0.6)",
        "7xl": "0px 4px 7px 0px rgba(0, 0, 0, 0.03)",
        "9xl": "0 10px 20px 0 rgb(46 56 220 / 5%)",
        "10xl": "0px 0px 4px rgba(19, 16, 34, 0.15)",
      },
      screens: {
        // min width
        "custom-xs": "576px",
        "custom-sm": "768px",
        "custom-md": "992px",
        "custom-lg": "1200px",
        "custom-2lg": "1300px",
        "custom-2xl": "1400px",
        "custom-3xl": "1600px",
        "custom-4xl": "1800px",
        "custom-5xl": "2000px",

        // max-width
        "max-xl": { max: "1599px" },
        "max-lg": { max: "1199px" },
        "max-md": { max: "991px" },
        "max-sm": { max: "767px" },
        "max-xs": { max: "575px" },
        "2xs": { max: "375px" },
        "max-xxs": { max: "360px" },
        "3xs": { max: "320px" },

        // min-width and max-width
        "custom-smb": { min: "992px", max: "1199px" },
        "custom-ssm": { min: "768px", max: "991px" },
      },
    },
  },
  plugins: [],
};
