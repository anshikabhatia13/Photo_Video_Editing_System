import {
  benefitIcon1,
  benefitIcon2,
  benefitIcon3,
  benefitIcon4,
  benefitImage3,
  benefitImage4,
  benefitImage5,
  benefitImage6,
  benefitImage7,
  benefitImage8,
  chromecast,
  disc02,
  discordBlack,
  facebook,
  file02,
  homeSmile,
  instagram,
  notification2,
  notification3,
  notification4,
  plusSquare,
  recording01,
  recording03,
  searchMd,
  sliders04,
  telegram,
  twitter,
  yourlogo,
} from "../assets";
export const navigation = [
  {
    id: "0",
    title: "Yolo-World",
    url: "#ImageSegmentationForm",
  },
  {
    id: "1",
    title: "RVOS",
    url: "#Form",
  },
  {
    id: "2",
    title: "U2Net",
    url: "#Unet",
  },

  // {
  //   id: "4",
  //   title: "New account",
  //   url: "#signup",
  //   onlyMobile: true,
  // },
  // {
  //   id: "5",
  //   title: "Sign in",
  //   url: "#login",
  //   onlyMobile: true,
  // },
];

export const heroIcons = [homeSmile, file02, searchMd, plusSquare];

export const notificationImages = [notification4, notification3, notification2];

export const companyLogos = [yourlogo, yourlogo, yourlogo, yourlogo, yourlogo];

export const brainwaveServices = [
  "Object Tracking",
  "Object Segmentation",
  "Text Referring",
];

export const brainwaveServicesIcons = [
  recording03,
  recording01,
  disc02,
  chromecast,
  sliders04,
];



export const collabText =
  "Introduced to discriminate semantic consensus between video-text pairs and impose it in positive pairs.";

export const benefits = [
  {
    id: "0",
    title: "Customize Background",
    text: "Upload image and select the background color!",
    backgroundUrl: "./src/assets/benefits/card-1.svg",
    iconUrl: benefitIcon1,
    imageUrl: benefitImage3,
    linkUrl: "src/models/unet", // Example internal link
  },
  {
    id: "1",
    title: "Choose your own background",
    text: "Upload image and background image and get the background defined by you!",
    backgroundUrl: "./src/assets/benefits/card-2.svg",
    iconUrl: benefitIcon2,
    imageUrl: benefitImage4,
    light: true,
  },
  {
    id: "2",
    title: "Your Custom Portrait Mode",
    text: "Enter what to focus, and get it portrait ready!",
    backgroundUrl: "./src/assets/benefits/card-3.svg",
    iconUrl: benefitIcon3,
    imageUrl: benefitImage5,
  },
  {
    id: "3",
    title: "Keep Selected Image Items",
    text: "Enter the items you want in image and customize the background!",
    backgroundUrl: "./src/assets/benefits/card-4.svg",
    iconUrl: benefitIcon4,
    imageUrl: benefitImage6,
    light: true,
  },
  {
    id: "4",
    title: "Segment Selected Video Items ",
    text: "Describe what to keep, remove the rest from video!",
    backgroundUrl: "./src/assets/benefits/card-5.svg",
    iconUrl: benefitIcon1,
    imageUrl: benefitImage7,
  },
  // {
  //   id: "5",
  //   title: "YOFO-Segmentation",
  //   text: "You Only Infer Once: Cross-Modal Meta-Transfer for Referring Video Object Segmentation",
  //   backgroundUrl: "./src/assets/benefits/card-6.svg",
  //   iconUrl: benefitIcon2,
  //   imageUrl: benefitImage8,
  // },
];

export const socials = [
  {
    id: "0",
    title: "Discord",
    iconUrl: discordBlack,
    url: "#",
  },
  {
    id: "1",
    title: "Twitter",
    iconUrl: twitter,
    url: "#",
  },
  {
    id: "2",
    title: "Instagram",
    iconUrl: instagram,
    url: "#",
  },
  {
    id: "3",
    title: "Telegram",
    iconUrl: telegram,
    url: "#",
  },
  {
    id: "4",
    title: "Facebook",
    iconUrl: facebook,
    url: "#",
  },
];
