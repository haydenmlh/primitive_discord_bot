from settings import *
from modpizzapi import *

class core(core_base):
    def __init__(self, client):
        core_base.__init__(self, client)
        self.pizza_profiles = dict()
        self.pizza_data = {
            'fname':None,
            'lname':None,
            'email':None,
            'phone':None,
            'street':None,
            'city':None,
            'province':None,
            'postal':None,
            'country':None
            }
        
    async def create_profile(self, prompt):
        data = self.pizza_data
        keys = data.keys()

        for key in keys:
            if data[key] == None:
                await self.send_message(prompt, f"Missing {key}, use 'set_{key}'")
                return
            
        fname = data['fname'].capitalize()
        lname = data['lname'].capitalize()
        email = data['email']
        phone = data['phone']
        street = data['street']
        city = data['city']
        province = data['province'].upper()
        postal = data['postal'].upper()
        country = data['country'].lower()

        try:
            customer = Customer(fname, lname, email, phone)

        except:
            await self.send_message(prompt, "Profile could not be created")
            return

        try:
            print(street, city, province, postal, country, sep=",")
            address = Address(street, city, province, postal, country)
            store = address.closest_store()

        except:
            await self.send_message(prompt, "Nearby store could not be located")
            return
        
        self.pizza_profiles['customer'] = customer
        self.pizza_profiles['address'] = address
        self.pizza_profiles['store'] = store

        await self.send_message(prompt, "Profile created successfully!")

    async def __set_attr(self, key, prompt):
        self.pizza_data[key] = " ".join(prompt.extra)
        
        lines = []
        for key, value in self.pizza_data.items():
            line = f"{key:<25}{value}"
            lines.append(line)

        await self.send_message(prompt, "\n".join(lines))    
        print(self.pizza_data)

    async def set_fname(self, prompt):
        await self.__set_attr('fname', prompt)

    async def set_lname(self, prompt):
        await self.__set_attr('lname', prompt)

    async def set_email(self, prompt):
        await self.__set_attr('email', prompt)

    async def set_phone(self, prompt):
        await self.__set_attr('phone', prompt)

    async def set_street(self, prompt):
        await self.__set_attr('street', prompt)

    async def set_city(self, prompt):
        await self.__set_attr('city', prompt)

    async def set_province(self, prompt):
        await self.__set_attr('province', prompt)

    async def set_postal(self, prompt):
        await self.__set_attr('postal', prompt)

    async def set_country(self, prompt):
        await self.__set_attr('country', prompt)

    async def menu_search(self, prompt):
        try:
            if 'store' not in self.pizza_profiles:
                await self.send_message(prompt, "Profile not created yet, use 'create_profile'")
                return
            
            store = self.pizza_profiles['store']
            menu = store.get_menu()

            results = menu.search(Name=" ".join(prompt.extra))
            
            lines = []
            for item in results:
                line = item['Code'].ljust(15)+'\t'+'$'+item['$'].ljust(5)+'\t'+item['Name']
                lines.append(line)

            await self.send_message(prompt, "\n".join(lines), cb=True)

        except:
            await self.send_message(prompt, "Error searching menu")
            
    async def order(self, prompt):
        try:
            items = prompt.extra

            store = self.pizza_profiles['store']
            customer = self.pizza_profiles['customer']
            address = self.pizza_profiles['address']
            country = self.pizza_data['country'].lower() 

            order = Order(store, customer, address, country)
            
            for item in items:
                order.add_item(item)

            if order.validate():
                await self.send_message(prompt, "Items added and order validated, success!")

            else:
                await self.send_message(prompt, "Items added, but order could not be validated...")
            
        except Exception as e:
            print(e)
            await self.send_message(prompt, "Error making order")

