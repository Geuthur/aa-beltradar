// AA Belt Radar
import { MenuItem } from "@/Menu/BaseMenu";
import type { MenuLinkItem, MenuProps } from "@/Menu/BaseMenu";

const BeltRadarMenu = ({ data }: MenuProps) => {
  const toPath = (link: string) => `/beltradar/${link}/`;

  const menuItems = Array.isArray(data)
    ? data.filter((item): item is MenuLinkItem => !!item.link)
    : [];

  return (
    <>
      {menuItems.map((item) => {
        return <MenuItem key={item.link} link={item} {...{ toPath }} />;
      })}
    </>
  );
};

export default BeltRadarMenu;
