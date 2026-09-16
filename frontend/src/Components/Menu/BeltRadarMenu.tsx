// AA Belt Radar
import { MenuItem } from "@/Components/Menu/BaseMenu";
import type { MenuLinkItem, MenuProps } from "@/Components/Menu/BaseMenu";

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
